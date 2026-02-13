"""
Task Parser for extracting task information from Microsoft Rewards dashboard
"""

import logging
from typing import List, Optional
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from tasks.task_base import TaskMetadata


class TaskParser:
    """Parser for Microsoft Rewards dashboard tasks"""
    
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.debug_mode = config.get("task_system.debug_mode", False) if config else False
    
    async def discover_tasks(self, page: Page) -> List[TaskMetadata]:
        """
        Navigate to dashboard and discover all available tasks
        
        Args:
            page: Playwright page object
            
        Returns:
            List of TaskMetadata objects
        """
        self.logger.info("Discovering tasks from dashboard...")
        
        try:
            # Navigate to rewards dashboard if not already there
            current_url = page.url
            if "rewards.microsoft.com" not in current_url:
                await page.goto(
                    "https://rewards.microsoft.com/",
                    wait_until="domcontentloaded",
                    timeout=15000
                )
            
            # Wait for dashboard to load
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(2000)
            
            # DIAGNOSTIC: Log current state
            self.logger.info(f"Current URL: {page.url}")
            try:
                page_title = await page.title()
                self.logger.info(f"Page title: {page_title}")
            except Exception:
                pass
            
            # Check if on login page
            if await self._is_login_page(page):
                self.logger.error("Detected login page, cannot discover tasks")
                return []
            
            # Parse tasks from the page
            tasks = await self._parse_tasks_from_page(page)
            
            self.logger.info(f"Discovered {len(tasks)} tasks")
            return tasks
            
        except PlaywrightTimeout:
            self.logger.error("Timeout while loading dashboard")
            return []
        except Exception as e:
            self.logger.error(f"Error discovering tasks: {e}")
            return []

    
    async def _is_login_page(self, page: Page) -> bool:
        """Check if currently on login page"""
        try:
            login_selectors = [
                'input[name="loginfmt"]',
                'input[type="email"]',
                '#i0116',
            ]
            
            for selector in login_selectors:
                element = await page.query_selector(selector)
                if element:
                    return True
            
            return False
        except Exception:
            return False
    
    async def _parse_tasks_from_page(self, page: Page) -> List[TaskMetadata]:
        """
        Parse task elements from the dashboard page (with fallback strategies)
        
        Args:
            page: Playwright page object
            
        Returns:
            List of TaskMetadata objects
        """
        tasks = []
        
        try:
            # Strategy 1: Try standard selectors
            elements = await self._try_standard_selectors(page)
            
            # Strategy 2: Try generic selectors if standard fails
            if not elements:
                self.logger.info("Standard selectors failed, trying generic selectors...")
                elements = await self._try_generic_selectors(page)
            
            # Strategy 3: Try link-based selectors as last resort
            if not elements:
                self.logger.info("Generic selectors failed, trying link-based selectors...")
                elements = await self._try_link_based_selectors(page)
            
            if not elements:
                self.logger.warning("No task elements found on page")
                
                # DIAGNOSTIC: Save screenshot and HTML for analysis (if debug mode enabled)
                if self.debug_mode:
                    import os
                    from datetime import datetime
                    os.makedirs("logs/diagnostics", exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    try:
                        # Save screenshot
                        screenshot_path = f"logs/diagnostics/no_tasks_{timestamp}.png"
                        await page.screenshot(path=screenshot_path, full_page=True)
                        self.logger.warning(f"📸 截图已保存: {screenshot_path}")
                        
                        # Save HTML
                        html = await page.content()
                        html_path = f"logs/diagnostics/no_tasks_{timestamp}.html"
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write(html)
                        self.logger.warning(f"📄 HTML已保存: {html_path}")
                        
                        self.logger.warning("⚠️ 诊断数据已收集 - 请检查这些文件以分析问题")
                    except Exception as e:
                        self.logger.error(f"保存诊断数据失败: {e}")
                else:
                    self.logger.info("💡 提示: 在config.yaml中启用task_system.debug_mode以保存诊断数据")
                
                return tasks
            
            self.logger.info(f"Found {len(elements)} potential task elements")
            
            # Parse each task element
            for i, element in enumerate(elements):
                try:
                    task_metadata = await self._extract_task_metadata(element, i)
                    if task_metadata:
                        tasks.append(task_metadata)
                        self.logger.debug(f"  ✓ Parsed task: {task_metadata.title} ({task_metadata.task_type}, {task_metadata.points}pts)")
                        
                        # DIAGNOSTIC: Log raw promotion_type for debugging
                        if task_metadata.promotion_type:
                            self.logger.debug(f"    Raw promotion_type: '{task_metadata.promotion_type}'")
                    else:
                        self.logger.debug(f"  ✗ Failed to parse task element {i}: metadata extraction returned None")
                except Exception as e:
                    self.logger.debug(f"  ✗ Failed to parse task element {i}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing tasks from page: {e}")
        
        return tasks
    
    async def _try_standard_selectors(self, page: Page) -> List:
        """Try standard task card selectors"""
        selectors = [
            'mee-card[data-bi-id]',
            '.mee-card',
            'mee-card',
        ]
        
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                self.logger.debug(f"Standard selector succeeded: {selector} ({len(elements)} elements)")
                return elements
        
        return []
    
    async def _try_generic_selectors(self, page: Page) -> List:
        """Try generic selectors as fallback"""
        selectors = [
            '[class*="daily-set"]',
            '[class*="promotion"]',
            '[class*="reward-card"]',
            '[class*="activity-card"]',
            '.c-card',
            '[data-bi-id]',
        ]
        
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            if elements and len(elements) > 0:
                self.logger.debug(f"Generic selector succeeded: {selector} ({len(elements)} elements)")
                return elements
        
        return []
    
    async def _try_link_based_selectors(self, page: Page) -> List:
        """Try link-based selectors as last resort"""
        selectors = [
            'a[href*="punchcard"]',
            'a[href*="quiz"]',
            'a[href*="urlreward"]',
            'a[href*="poll"]',
        ]
        
        all_elements = []
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                self.logger.debug(f"Link selector found: {selector} ({len(elements)} elements)")
                all_elements.extend(elements)
        
        return all_elements
    
    async def _extract_task_metadata(self, element, index: int = 0) -> Optional[TaskMetadata]:
        """
        Extract metadata from a task element
        
        Args:
            element: Playwright element handle
            index: Element index (for generating fallback ID)
            
        Returns:
            TaskMetadata object or None if extraction fails
        """
        try:
            # Extract task ID
            task_id = await element.get_attribute('data-bi-id')
            if not task_id:
                task_id = await element.get_attribute('id')
            if not task_id:
                task_id = f"task_{index}"
            
            # Extract promotion type - ENHANCED with more strategies
            promotion_type = None
            
            # Strategy 1: data-bi-type attribute
            promotion_type = await element.get_attribute('data-bi-type')
            
            # Strategy 2: data-promotion-type attribute
            if not promotion_type:
                promotion_type = await element.get_attribute('data-promotion-type')
            
            # Strategy 3: class names (look for task type in class)
            if not promotion_type:
                class_name = await element.get_attribute('class')
                if class_name:
                    class_lower = class_name.lower()
                    if 'quiz' in class_lower:
                        promotion_type = 'quiz'
                    elif 'poll' in class_lower:
                        promotion_type = 'poll'
                    elif 'urlreward' in class_lower or 'url-reward' in class_lower:
                        promotion_type = 'urlreward'
            
            # Strategy 4: Check href for clues
            if not promotion_type:
                href = await element.get_attribute('href')
                if not href:
                    # Look for child link
                    link_element = await element.query_selector('a[href]')
                    if link_element:
                        href = await link_element.get_attribute('href')
                
                if href:
                    href_lower = href.lower()
                    if 'quiz' in href_lower:
                        promotion_type = 'quiz'
                    elif 'poll' in href_lower:
                        promotion_type = 'poll'
                    elif 'urlreward' in href_lower:
                        promotion_type = 'urlreward'
                    elif 'punchcard' in href_lower:
                        promotion_type = 'urlreward'  # Punchcards are usually URL rewards
            
            # Strategy 5: Check aria-label
            if not promotion_type:
                aria_label = await element.get_attribute('aria-label')
                if aria_label:
                    aria_lower = aria_label.lower()
                    if 'quiz' in aria_lower or '测验' in aria_lower:
                        promotion_type = 'quiz'
                    elif 'poll' in aria_lower or '投票' in aria_lower:
                        promotion_type = 'poll'
            
            # Strategy 6: Check inner text for keywords
            if not promotion_type:
                try:
                    inner_text = await element.inner_text()
                    if inner_text:
                        text_lower = inner_text.lower()
                        if 'quiz' in text_lower or '测验' in text_lower:
                            promotion_type = 'quiz'
                        elif 'poll' in text_lower or '投票' in text_lower:
                            promotion_type = 'poll'
                except Exception:
                    pass
            
            # Default to urlreward if still unknown (most common type)
            if not promotion_type:
                promotion_type = 'urlreward'
            
            # Extract title
            title = await self._extract_title(element)
            if not title:
                title = f"Task {index + 1}"
            
            # Extract points
            points = await self._extract_points(element)
            
            # Check if completed
            is_completed = await self._is_task_completed(element)
            
            # Extract destination URL
            destination_url = await self._extract_destination_url(element)
            
            # Determine task type from promotion type
            task_type = self._determine_task_type(promotion_type)
            
            return TaskMetadata(
                task_id=task_id,
                task_type=task_type,
                title=title,
                points=points,
                is_completed=is_completed,
                destination_url=destination_url,
                promotion_type=promotion_type
            )
            
        except Exception as e:
            self.logger.debug(f"Failed to extract task metadata: {e}")
            return None
    
    async def _extract_title(self, element) -> Optional[str]:
        """Extract task title with multiple fallback strategies"""
        title_selectors = [
            '.mee-card-title',
            '[class*="title"]',
            'h3',
            'h4',
            '.card-title',
        ]
        
        for selector in title_selectors:
            try:
                title_element = await element.query_selector(selector)
                if title_element:
                    title = await title_element.inner_text()
                    if title and title.strip():
                        return title.strip()
            except Exception:
                continue
        
        # Fallback: get element text content
        try:
            text = await element.inner_text()
            if text and text.strip():
                return text.strip()[:50]  # Limit to 50 chars
        except Exception:
            pass
        
        return None
    
    async def _extract_points(self, element) -> int:
        """Extract points value with fallback"""
        points_selectors = [
            '.mee-card-points',
            '[class*="points"]',
            '[class*="point-value"]',
        ]
        
        for selector in points_selectors:
            try:
                points_element = await element.query_selector(selector)
                if points_element:
                    points_text = await points_element.inner_text()
                    points = self._parse_points(points_text)
                    if points > 0:
                        return points
            except Exception:
                continue
        
        # Fallback: try to extract from entire element text
        try:
            text = await element.inner_text()
            points = self._parse_points(text)
            if points > 0:
                return points
        except Exception:
            pass
        
        return 0
    
    async def _extract_destination_url(self, element) -> Optional[str]:
        """Extract destination URL"""
        try:
            # Check if element itself is a link
            href = await element.get_attribute('href')
            if href:
                return href
            
            # Look for child link
            link_element = await element.query_selector('a[href]')
            if link_element:
                href = await link_element.get_attribute('href')
                return href
            
            return None
        except Exception:
            return None
    
    def _parse_points(self, points_text: str) -> int:
        """Parse points value from text"""
        try:
            # Extract numeric value from text like "10 points" or "+10"
            import re
            match = re.search(r'(\d+)', points_text)
            return int(match.group(1)) if match else 0
        except Exception:
            return 0
    
    async def _is_task_completed(self, element) -> bool:
        """Check if task is completed (enhanced with more indicators)"""
        try:
            # Check for completion indicators
            completed_indicators = [
                '.mee-icon-AddMedium',  # Checkmark icon
                '[class*="completed"]',
                '[class*="done"]',
                '[class*="check"]',  # Added
                '[aria-label*="Completed"]',
                '[aria-label*="完成"]',  # Added for Chinese
            ]
            
            for indicator in completed_indicators:
                completed_element = await element.query_selector(indicator)
                if completed_element:
                    return True
            
            # Check aria-label attribute
            aria_label = await element.get_attribute('aria-label')
            if aria_label and ('completed' in aria_label.lower() or '完成' in aria_label):
                return True
            
            return False
        except Exception:
            return False
    
    def _determine_task_type(self, promotion_type: str) -> str:
        """
        Determine task type from promotion type
        
        Args:
            promotion_type: Raw promotion type from element
            
        Returns:
            Standardized task type
        """
        promotion_type_lower = promotion_type.lower()
        
        # Quiz tasks
        if 'quiz' in promotion_type_lower:
            return 'quiz'
        
        # Poll tasks
        elif 'poll' in promotion_type_lower:
            return 'poll'
        
        # URL reward tasks (most common)
        elif 'urlreward' in promotion_type_lower or 'url' in promotion_type_lower:
            return 'urlreward'
        
        # Special tasks
        elif 'clippy' in promotion_type_lower or 'findclippy' in promotion_type_lower:
            return 'urlreward'  # Treat as URL task
        
        # Default: treat unknown types as URL reward tasks
        # Most tasks are just "click and visit" which is what urlreward does
        else:
            return 'urlreward'
