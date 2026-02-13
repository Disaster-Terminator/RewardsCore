"""
搜索引擎模块
执行搜索任务，协调各个组件
"""

import random
import asyncio
import logging
from typing import Optional
from playwright.async_api import Page
from cookie_handler import CookieHandler

logger = logging.getLogger(__name__)


class SearchEngine:
    """搜索引擎类"""
    
    BING_URL = "https://www.bing.com"
    
    def __init__(self, config, term_generator, anti_ban, monitor=None):
        """
        初始化搜索引擎
        
        Args:
            config: ConfigManager 实例
            term_generator: SearchTermGenerator 实例
            anti_ban: AntiBanModule 实例
            monitor: StateMonitor 实例（可选）
        """
        self.config = config
        self.term_generator = term_generator
        self.anti_ban = anti_ban
        self.monitor = monitor
        
        logger.info("搜索引擎初始化完成")
    
    async def navigate_to_bing(self, page: Page) -> bool:
        """
        导航到 Bing 搜索页面
        
        Args:
            page: Playwright Page 对象
            
        Returns:
            是否成功
        """
        try:
            logger.debug(f"导航到 Bing: {self.BING_URL}")
            await page.goto(self.BING_URL, wait_until="networkidle", timeout=30000)
            return True
        except Exception as e:
            logger.error(f"导航到 Bing 失败: {e}")
            return False
    
    async def perform_single_search(self, page: Page, term: str) -> bool:
        """
        执行单次搜索
        
        Args:
            page: Playwright Page 对象
            term: 搜索词
            
        Returns:
            是否成功
        """
        try:
            logger.info(f"搜索: {term}")
            
            # 1. 检查当前页面，如果需要则导航到 Bing
            current_url = page.url
            need_navigate = False
            
            if "rewards" in current_url:
                logger.debug("当前在 rewards 页面，需要导航到 Bing")
                need_navigate = True
            elif "bing.com" not in current_url:
                logger.debug("不在 Bing 页面，需要导航")
                need_navigate = True
            else:
                logger.debug(f"已在 Bing 页面: {current_url}")
            
            if need_navigate:
                try:
                    await page.goto(self.BING_URL, wait_until="domcontentloaded", timeout=20000)
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"导航到 Bing 失败: {e}")
                    return False
            
            # 2. 快速处理 Cookie 弹窗（如果存在）
            try:
                handled = await CookieHandler.handle_cookie_popup(page)
                if handled:
                    await asyncio.sleep(1)
                    # 如果被重定向，再次导航
                    if "rewards" in page.url:
                        await page.goto(self.BING_URL, wait_until="domcontentloaded", timeout=20000)
                        await asyncio.sleep(1)
            except Exception as e:
                logger.debug(f"处理 Cookie 弹窗时出错: {e}")
            
            # 3. 找到搜索框
            search_box_selectors = [
                "input[name='q']",
                "input#sb_form_q",
                "textarea[name='q']",
                "input[type='search']",
            ]
            
            search_box = None
            
            for selector in search_box_selectors:
                try:
                    search_box = await page.wait_for_selector(
                        selector, 
                        timeout=5000, 
                        state="visible"
                    )
                    if search_box:
                        logger.debug(f"找到搜索框: {selector}")
                        break
                except:
                    continue
            
            if not search_box:
                logger.error("未找到搜索框")
                try:
                    await page.screenshot(path="screenshots/search_box_not_found.png", full_page=True)
                    logger.info(f"已保存截图，当前 URL: {page.url}")
                except:
                    pass
                return False
            
            # 4. 清空搜索框
            await search_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await asyncio.sleep(0.2)
            
            # 5. 模拟人类打字（逐字符输入）
            logger.debug(f"开始输入搜索词: {term}")
            for char in term:
                await page.keyboard.type(char)
                # 每个字符之间随机延迟 50-150ms
                delay = random.uniform(0.05, 0.15)
                await asyncio.sleep(delay)
                
                # 偶尔有更长的停顿（模拟思考）
                if random.random() < 0.1:  # 10% 概率
                    think_delay = random.uniform(0.2, 0.5)
                    await asyncio.sleep(think_delay)
            
            logger.debug("搜索词输入完成")
            
            # 6. 提交搜索
            await page.keyboard.press("Enter")
            
            # 7. 等待搜索结果加载
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
            except:
                logger.warning("等待页面加载超时，继续...")
            
            await asyncio.sleep(random.uniform(1, 2))
            
            # 8. 模拟人类浏览行为
            await self.anti_ban.simulate_human_scroll(page)
            
            # 9. 随机点击搜索结果（30% 概率）
            if random.random() < 0.3:
                await self._click_random_result(page)
            
            # 10. 随机翻页（20% 概率）
            if random.random() < 0.2:
                await self._random_pagination(page)
            
            logger.info(f"✓ 搜索完成: {term}")
            return True
            
        except Exception as e:
            logger.error(f"搜索失败 '{term}': {e}")
            return False
    
    async def _click_random_result(self, page: Page) -> None:
        """
        随机点击一个搜索结果（增加真实性）
        
        Args:
            page: Playwright Page 对象
        """
        try:
            logger.debug("尝试点击搜索结果...")
            
            # 查找搜索结果链接
            result_selectors = [
                "li.b_algo h2 a",
                "div.b_algo h2 a",
                "h2 a[href]",
            ]
            
            result_links = []
            for selector in result_selectors:
                try:
                    links = await page.query_selector_all(selector)
                    if links:
                        result_links = links
                        break
                except:
                    continue
            
            if not result_links:
                logger.debug("未找到搜索结果链接")
                return
            
            # 随机选择一个结果（通常选择前 5 个）
            available_links = result_links[:min(5, len(result_links))]
            link = random.choice(available_links)
            
            # 获取链接文本和 URL
            try:
                link_text = await link.text_content()
                link_url = await link.get_attribute("href")
                logger.debug(f"点击搜索结果: {link_text[:50]}...")
            except:
                link_url = None
            
            # 保存当前页面的 URL（用于返回）
            original_url = page.url
            
            # 点击链接（使用 click 并等待导航）
            # 注意：使用 modifiers=[] 确保不会在新标签页打开
            try:
                # 监听新页面打开事件
                context = page.context
                
                # 点击链接
                try:
                    # 尝试监听新标签页
                    new_page_promise = context.wait_for_event("page", timeout=2000)
                    await link.click(modifiers=[], timeout=5000)
                    
                    # 检查是否打开了新标签页
                    try:
                        new_page = await new_page_promise
                        # 如果打开了新标签页，等待一下再关闭（避免 stealth 脚本冲突）
                        logger.debug("检测到新标签页，关闭并在当前页面打开")
                        await asyncio.sleep(0.5)  # 等待 stealth 脚本完成或超时
                        try:
                            await new_page.close()
                        except:
                            pass  # 忽略关闭错误
                        
                        # 在当前页面导航
                        if link_url:
                            await page.goto(link_url, wait_until="domcontentloaded", timeout=10000)
                    except asyncio.TimeoutError:
                        # 没有新标签页，正常在当前页面打开
                        pass
                    
                except Exception as e:
                    logger.debug(f"点击失败: {e}")
                    # 尝试直接导航
                    if link_url:
                        await page.goto(link_url, wait_until="domcontentloaded", timeout=10000)
                    else:
                        return
                
            except Exception as e:
                logger.debug(f"导航失败: {e}")
                return
            
            # 等待页面加载
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
            except:
                pass
            
            # 在页面上停留一小段时间
            stay_time = random.uniform(2, 4)
            await asyncio.sleep(stay_time)
            
            # 滚动一下
            await self.anti_ban.simulate_human_scroll(page)
            
            # 返回搜索结果（使用后退按钮）
            try:
                await page.go_back(wait_until="domcontentloaded", timeout=10000)
                await asyncio.sleep(random.uniform(1, 2))
            except Exception as e:
                logger.debug(f"后退失败，直接导航回搜索页: {e}")
                # 如果后退失败，直接导航回原始 URL
                try:
                    await page.goto(original_url, wait_until="domcontentloaded", timeout=10000)
                    await asyncio.sleep(1)
                except:
                    pass
            
            logger.debug("✓ 搜索结果点击完成")
            
        except Exception as e:
            logger.debug(f"点击搜索结果失败: {e}")
            # 确保我们回到搜索页面
            try:
                if "bing.com/search" not in page.url:
                    await page.goto(self.BING_URL, wait_until="domcontentloaded", timeout=10000)
            except:
                pass
    
    async def _random_pagination(self, page: Page) -> None:
        """
        随机翻页（增加真实性）
        
        Args:
            page: Playwright Page 对象
        """
        try:
            logger.debug("尝试翻页...")
            
            # 查找"下一页"按钮
            next_page_selectors = [
                "a[title='Next page']",
                "a.sb_pagN",
                "a:has-text('Next')",
            ]
            
            next_button = None
            for selector in next_page_selectors:
                try:
                    next_button = await page.query_selector(selector)
                    if next_button:
                        break
                except:
                    continue
            
            if not next_button:
                logger.debug("未找到翻页按钮")
                return
            
            # 点击下一页
            await next_button.click()
            
            # 等待页面加载
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass
            
            await asyncio.sleep(random.uniform(1, 2))
            
            # 滚动浏览
            await self.anti_ban.simulate_human_scroll(page)
            
            # 返回第一页
            await page.go_back()
            await asyncio.sleep(random.uniform(1, 2))
            
            logger.debug("✓ 翻页完成")
            
        except Exception as e:
            logger.debug(f"翻页失败: {e}")
    
    async def execute_desktop_searches(self, page: Page, count: int) -> int:
        """
        执行桌面端搜索
        
        Args:
            page: Playwright Page 对象
            count: 搜索次数
            
        Returns:
            成功的搜索次数
        """
        logger.info(f"开始执行 {count} 次桌面搜索...")
        
        success_count = 0
        
        for i in range(count):
            # 获取搜索词
            term = self.term_generator.get_random_term()
            
            logger.info(f"[{i+1}/{count}] 搜索: {term}")
            
            # 执行搜索
            if await self.perform_single_search(page, term):
                success_count += 1
            else:
                logger.warning(f"搜索 {i+1} 失败，继续...")
            
            # 等待随机时间（最后一次搜索不需要等待）
            if i < count - 1:
                wait_time = self.anti_ban.get_random_wait_time()
                logger.debug(f"等待 {wait_time:.1f} 秒...")
                await asyncio.sleep(wait_time)
        
        logger.info(f"✓ 桌面搜索完成: {success_count}/{count} 成功")
        return success_count
    
    async def execute_mobile_searches(self, page: Page, count: int) -> int:
        """
        执行移动端搜索
        
        Args:
            page: Playwright Page 对象
            count: 搜索次数
            
        Returns:
            成功的搜索次数
        """
        logger.info(f"开始执行 {count} 次移动搜索...")
        
        success_count = 0
        
        for i in range(count):
            # 获取搜索词
            term = self.term_generator.get_random_term()
            
            logger.info(f"[{i+1}/{count}] 搜索: {term}")
            
            # 执行搜索
            if await self.perform_single_search(page, term):
                success_count += 1
            else:
                logger.warning(f"搜索 {i+1} 失败，继续...")
            
            # 等待随机时间
            if i < count - 1:
                wait_time = self.anti_ban.get_random_wait_time()
                logger.debug(f"等待 {wait_time:.1f} 秒...")
                await asyncio.sleep(wait_time)
        
        logger.info(f"✓ 移动搜索完成: {success_count}/{count} 成功")
        return success_count
