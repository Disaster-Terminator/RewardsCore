"""
账户管理器模块
管理登录状态和会话持久化
"""

import os
import json
import logging
from typing import Optional, Dict
from pathlib import Path
from playwright.async_api import Page, BrowserContext

logger = logging.getLogger(__name__)


class AccountManager:
    """账户管理器类"""
    
    def __init__(self, config):
        """
        初始化账户管理器
        
        Args:
            config: ConfigManager 实例
        """
        self.config = config
        self.storage_state_path = config.get("account.storage_state_path", "storage_state.json")
        self.login_url = config.get("account.login_url", "https://rewards.microsoft.com/")
        
        logger.info(f"账户管理器初始化完成: {self.storage_state_path}")
    
    async def load_session(self) -> Optional[Dict]:
        """
        加载保存的会话状态
        
        Returns:
            会话状态字典，失败返回 None
        """
        if not os.path.exists(self.storage_state_path):
            logger.info(f"会话文件不存在: {self.storage_state_path}")
            return None
        
        try:
            with open(self.storage_state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # 验证会话状态格式
            if not isinstance(state, dict):
                logger.error("会话状态格式无效")
                return None
            
            if "cookies" not in state:
                logger.error("会话状态缺少 cookies")
                return None
            
            cookie_count = len(state.get("cookies", []))
            logger.info(f"✓ 加载会话状态成功: {cookie_count} 个 cookies")
            
            return state
            
        except json.JSONDecodeError as e:
            logger.error(f"会话文件 JSON 解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"加载会话状态失败: {e}")
            return None
    
    async def save_session(self, context: BrowserContext) -> bool:
        """
        保存会话状态到磁盘
        
        Args:
            context: BrowserContext 实例
            
        Returns:
            是否成功
        """
        try:
            # 获取会话状态
            state = await context.storage_state()
            
            # 确保目录存在
            Path(self.storage_state_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 保存到文件
            with open(self.storage_state_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            cookie_count = len(state.get("cookies", []))
            file_size = os.path.getsize(self.storage_state_path)
            
            logger.info(f"✓ 会话状态已保存: {self.storage_state_path}")
            logger.info(f"  Cookies: {cookie_count}, 文件大小: {file_size} bytes")
            
            return True
            
        except Exception as e:
            logger.error(f"保存会话状态失败: {e}")
            return False
    
    async def is_logged_in(self, page: Page) -> bool:
        """
        检查是否已登录
        
        Args:
            page: Playwright Page 对象
            
        Returns:
            是否已登录
        """
        try:
            logger.info("检查登录状态...")
            
            # 导航到登录页面（使用更短的超时）
            try:
                await page.goto(self.login_url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                logger.warning(f"页面导航超时，尝试继续: {e}")
            
            # 等待页面加载
            await page.wait_for_timeout(2000)
            
            # 检查是否存在登录后的元素
            # 方法 1: 检查积分显示元素
            logged_in_selectors = [
                "span.mee-rewards-user-status-balance",
                "div[class*='user-status']",
                "div[class*='rewards-balance']",
                "[data-bi-id='rewards-balance']",
                "div#daily-sets",  # 每日任务面板
                "mee-rewards-dashboard",  # Dashboard 组件
            ]
            
            for selector in logged_in_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=3000)
                    if element:
                        logger.info("✓ 用户已登录")
                        return True
                except:
                    continue
            
            # 方法 2: 检查是否有登录按钮（如果有，说明未登录）
            login_selectors = [
                "a[href*='login']",
                "button:has-text('Sign in')",
                "a:has-text('Sign in')",
            ]
            
            for selector in login_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text and ("sign in" in text.lower() or "login" in text.lower()):
                            logger.info("✗ 用户未登录（发现登录按钮）")
                            return False
                except:
                    continue
            
            # 方法 3: 检查 URL
            current_url = page.url
            if "login" in current_url.lower():
                logger.info("✗ 用户未登录（在登录页面）")
                return False
            
            # 方法 4: 检查页面内容
            try:
                content = await page.content()
                if "rewards" in content.lower() and "dashboard" in content.lower():
                    logger.info("✓ 用户已登录（从页面内容判断）")
                    return True
            except:
                pass
            
            # 如果无法确定，假设已登录（因为有 storage_state）
            logger.warning("⚠ 无法确定登录状态，假设已登录")
            return True
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            # 如果检查失败，假设已登录
            return True
    
    async def wait_for_manual_login(self, page: Page, timeout: int = 300) -> bool:
        """
        等待用户手动登录
        
        Args:
            page: Playwright Page 对象
            timeout: 超时时间（秒）
            
        Returns:
            是否登录成功
        """
        import asyncio
        
        logger.info("=" * 60)
        logger.info("请在浏览器中手动登录")
        logger.info("=" * 60)
        logger.info(f"超时时间: {timeout} 秒")
        
        # 导航到登录页面
        await page.goto(self.login_url, wait_until="networkidle", timeout=60000)
        
        # 等待登录完成
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # 检查超时
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.error(f"等待登录超时（{timeout}秒）")
                return False
            
            # 检查是否已登录
            if await self.is_logged_in(page):
                logger.info("✓ 登录成功！")
                return True
            
            # 等待一段时间再检查
            await asyncio.sleep(2)
    
    def get_storage_state_path(self) -> str:
        """
        获取会话状态文件路径
        
        Returns:
            文件路径
        """
        return self.storage_state_path
    
    def session_exists(self) -> bool:
        """
        检查会话文件是否存在
        
        Returns:
            是否存在
        """
        exists = os.path.exists(self.storage_state_path)
        
        if exists:
            file_size = os.path.getsize(self.storage_state_path)
            logger.debug(f"会话文件存在: {self.storage_state_path} ({file_size} bytes)")
        else:
            logger.debug(f"会话文件不存在: {self.storage_state_path}")
        
        return exists
    
    async def refresh_session(self, page: Page, context: BrowserContext) -> bool:
        """
        刷新会话（重新登录并保存）
        
        Args:
            page: Playwright Page 对象
            context: BrowserContext 实例
            
        Returns:
            是否成功
        """
        logger.info("开始刷新会话...")
        
        # 等待手动登录
        if await self.wait_for_manual_login(page):
            # 保存新的会话状态
            return await self.save_session(context)
        
        return False
