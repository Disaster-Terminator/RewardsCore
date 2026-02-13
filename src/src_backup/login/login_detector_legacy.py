"""
登录状态检测器模块
提供多重检测方法来确定用户登录状态
"""

import asyncio
import logging
import time
import json
from typing import Optional, Dict, Any, List
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class LoginStatusCache:
    """登录状态缓存类"""
    
    def __init__(self, cache_duration: int = 300):  # 5分钟缓存
        """
        初始化缓存
        
        Args:
            cache_duration: 缓存持续时间（秒）
        """
        self.cache_duration = cache_duration
        self.cached_status: Optional[bool] = None
        self.cache_timestamp: Optional[float] = None
        self.cache_reason: Optional[str] = None
    
    def get_cached_status(self) -> Optional[bool]:
        """
        获取缓存的登录状态
        
        Returns:
            缓存的状态或None（如果过期）
        """
        if (self.cached_status is not None and 
            self.cache_timestamp is not None and
            time.time() - self.cache_timestamp < self.cache_duration):
            return self.cached_status
        return None
    
    def set_cached_status(self, status: bool, reason: str = ""):
        """
        设置缓存状态
        
        Args:
            status: 登录状态
            reason: 检测原因
        """
        self.cached_status = status
        self.cache_timestamp = time.time()
        self.cache_reason = reason
    
    def clear_cache(self):
        """清除缓存"""
        self.cached_status = None
        self.cache_timestamp = None
        self.cache_reason = None


class LoginDetector:
    """登录状态检测器类"""
    
    # 登录状态检测选择器
    LOGGED_IN_SELECTORS = [
        # 用户头像/菜单
        "button[id*='mectrl']",                    # Microsoft控制按钮
        "div[id*='mectrl']",                       # Microsoft控制区域
        "button[aria-label*='Account manager']",   # 账户管理器
        "div.id_avatar",                           # 头像
        "img[alt*='profile']",                     # 个人资料图片
        "button[data-testid='account-menu']",      # 账户菜单
        
        # 用户信息显示
        "div[data-testid='user-info']",            # 用户信息
        "span[data-testid='username']",            # 用户名
        "div.user-name",                           # 用户名区域
        
        # Microsoft特定元素
        "div#mectrl_main",                         # Microsoft主控制
        "button#mectrl_headerPicture",             # 头像按钮
        "div.mectrl_theme",                        # Microsoft主题
    ]
    
    LOGGED_OUT_SELECTORS = [
        # 登录按钮（更精确的选择器，避免误判）
        "a[href*='login.live.com']",               # Microsoft登录链接
        "a[href*='login.microsoftonline.com']",    # Microsoft在线登录
        "button[data-testid='sign-in']",           # 登录测试ID
        "a[href*='microsoft.com/oauth']",          # OAuth登录
        
        # 主要登录按钮（需要在导航栏或头部）
        "header a:has-text('Sign in')",            # 头部登录链接
        "nav a:has-text('Sign in')",               # 导航栏登录链接
        "header button:has-text('Sign in')",       # 头部登录按钮
        "nav button:has-text('Log in')",           # 导航栏登录按钮
    ]
    
    def __init__(self, config=None):
        """
        初始化登录检测器
        
        Args:
            config: 配置管理器实例
        """
        self.config = config
        self.cache = LoginStatusCache()
        
        # 检测方法权重（用于多数投票）
        self.method_weights = {
            "user_element": 3,      # 用户元素检测权重最高
            "cookie": 2,            # Cookie检测
            "api_response": 2,      # API响应检测
            "page_content": 1,      # 页面内容检测
        }
        
        logger.info("登录状态检测器初始化完成")
    
    async def detect_login_status(self, page: Page, use_cache: bool = True) -> bool:
        """
        检测登录状态（主入口方法）
        
        Args:
            page: Playwright页面对象
            use_cache: 是否使用缓存
            
        Returns:
            是否已登录
        """
        # 检查缓存
        if use_cache:
            cached_status = self.cache.get_cached_status()
            if cached_status is not None:
                logger.debug(f"使用缓存的登录状态: {cached_status} ({self.cache.cache_reason})")
                return cached_status
        
        logger.info("开始多重登录状态检测...")
        
        # 执行多种检测方法
        detection_results = {}
        
        # 1. 用户元素检测
        try:
            logger.debug("=" * 50)
            logger.debug("执行用户元素检测...")
            result = await self._detect_by_user_elements(page)
            detection_results["user_element"] = result
            logger.info(f"用户元素检测结果: {result}")
        except Exception as e:
            logger.warning(f"用户元素检测失败: {e}")
            detection_results["user_element"] = None
        
        # 2. Cookie检测
        try:
            logger.debug("=" * 50)
            logger.debug("执行Cookie检测...")
            result = await self._detect_by_cookies(page)
            detection_results["cookie"] = result
            logger.info(f"Cookie检测结果: {result}")
        except Exception as e:
            logger.warning(f"Cookie检测失败: {e}")
            detection_results["cookie"] = None
        
        # 3. API响应检测
        try:
            logger.debug("=" * 50)
            logger.debug("执行API响应检测...")
            result = await self._detect_by_api_response(page)
            detection_results["api_response"] = result
            logger.info(f"API响应检测结果: {result}")
        except Exception as e:
            logger.warning(f"API响应检测失败: {e}")
            detection_results["api_response"] = None
        
        # 4. 页面内容检测
        try:
            logger.debug("=" * 50)
            logger.debug("执行页面内容检测...")
            result = await self._detect_by_page_content(page)
            detection_results["page_content"] = result
            logger.info(f"页面内容检测结果: {result}")
        except Exception as e:
            logger.warning(f"页面内容检测失败: {e}")
            detection_results["page_content"] = None
        
        logger.debug("=" * 50)
        
        # 使用多数投票决定最终状态
        final_status = self._vote_on_status(detection_results)
        
        # 缓存结果
        reason = f"多重检测: {detection_results}"
        self.cache.set_cached_status(final_status, reason)
        
        logger.info(f"=" * 50)
        logger.info(f"登录状态检测完成: {'已登录' if final_status else '未登录'}")
        logger.info(f"检测结果汇总: {detection_results}")
        logger.info(f"=" * 50)
        return final_status
    
    async def _detect_by_user_elements(self, page: Page) -> Optional[bool]:
        """
        通过用户界面元素检测登录状态
        
        Args:
            page: Playwright页面对象
            
        Returns:
            登录状态或None（如果无法确定）
        """
        logger.debug(f"[用户元素检测] 当前URL: {page.url}")
        
        # 检查登录状态元素
        for selector in self.LOGGED_IN_SELECTORS:
            try:
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    logger.debug(f"[用户元素检测] 选择器 {selector}: 存在={True}, 可见={is_visible}")
                    if is_visible:
                        logger.info(f"[用户元素检测] ✓ 找到登录元素: {selector}")
                        return True
            except Exception as e:
                logger.debug(f"[用户元素检测] 选择器 {selector} 检查失败: {e}")
                continue
        
        # 检查登出状态元素
        for selector in self.LOGGED_OUT_SELECTORS:
            try:
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    logger.debug(f"[用户元素检测] 选择器 {selector}: 存在={True}, 可见={is_visible}")
                    if is_visible:
                        logger.info(f"[用户元素检测] ✗ 找到登出元素: {selector}")
                        return False
            except Exception as e:
                logger.debug(f"[用户元素检测] 选择器 {selector} 检查失败: {e}")
                continue
        
        logger.debug("[用户元素检测] 未找到明确的登录/登出元素")
        return None
    
    async def _detect_by_cookies(self, page: Page) -> Optional[bool]:
        """
        通过Cookie检测登录状态
        
        Args:
            page: Playwright页面对象
            
        Returns:
            登录状态或None（如果无法确定）
        """
        try:
            cookies = await page.context.cookies()
            logger.debug(f"[Cookie检测] 总共有 {len(cookies)} 个Cookie")
            
            # 检查Microsoft相关的认证Cookie
            auth_cookies = [
                "MSPOK",           # Microsoft认证Cookie
                "MSPRequ",         # Microsoft请求Cookie
                "MSCC",            # Microsoft Cookie同意
                "MUID",            # Microsoft用户ID
                "_EDGE_S",         # Edge同步Cookie
                "_EDGE_V",         # Edge版本Cookie
            ]
            
            found_auth_cookies = []
            for cookie in cookies:
                if cookie['name'] in auth_cookies:
                    found_auth_cookies.append(cookie['name'])
                    logger.debug(f"[Cookie检测] ✓ 找到认证Cookie: {cookie['name']}")
            
            logger.info(f"[Cookie检测] 找到 {len(found_auth_cookies)} 个认证Cookie: {found_auth_cookies}")
            
            # 如果找到多个认证Cookie，可能已登录
            if len(found_auth_cookies) >= 2:
                logger.info(f"[Cookie检测] ✓ 认证Cookie数量充足，判定为已登录")
                return True
            elif len(found_auth_cookies) == 0:
                logger.info(f"[Cookie检测] ✗ 未找到认证Cookie，判定为未登录")
                return False
            
            logger.debug(f"[Cookie检测] 认证Cookie数量不足，无法判定")
            return None
            
        except Exception as e:
            logger.warning(f"[Cookie检测] 检测出错: {e}")
            return None
    
    async def _detect_by_api_response(self, page: Page) -> Optional[bool]:
        """
        通过API响应检测登录状态
        
        Args:
            page: Playwright页面对象
            
        Returns:
            登录状态或None（如果无法确定）
        """
        try:
            # 监听网络请求
            responses = []
            
            def handle_response(response):
                if any(pattern in response.url for pattern in 
                       ['api', 'rewards', 'account', 'profile']):
                    responses.append(response)
            
            page.on("response", handle_response)
            
            # 刷新页面或导航到检测页面
            try:
                await page.reload(wait_until="networkidle", timeout=10000)
            except Exception:
                pass
            
            # 检查响应
            for response in responses:
                try:
                    if response.status == 200:
                        # 检查响应头
                        headers = response.headers
                        if 'set-cookie' in headers:
                            cookie_header = headers['set-cookie']
                            if any(auth_name in cookie_header for auth_name in 
                                   ['MSPOK', 'MSPRequ', 'auth']):
                                return True
                        
                        # 检查响应内容（如果是JSON）
                        try:
                            if 'application/json' in response.headers.get('content-type', ''):
                                content = await response.text()
                                data = json.loads(content)
                                
                                # 检查常见的用户信息字段
                                if any(field in data for field in 
                                       ['user', 'account', 'profile', 'authenticated']):
                                    return True
                        except Exception:
                            pass
                    
                    elif response.status == 401:
                        # 未授权响应通常表示未登录
                        return False
                
                except Exception as e:
                    logger.debug(f"检查响应失败: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"API响应检测出错: {e}")
            return None
        finally:
            # 移除事件监听器
            try:
                page.remove_listener("response", handle_response)
            except Exception:
                pass
    
    async def _detect_by_page_content(self, page: Page) -> Optional[bool]:
        """
        通过页面内容检测登录状态
        
        Args:
            page: Playwright页面对象
            
        Returns:
            登录状态或None（如果无法确定）
        """
        try:
            # 获取页面内容
            content = await page.content()
            title = await page.title()
            url = page.url
            
            # 检查URL
            if any(pattern in url.lower() for pattern in 
                   ['login', 'signin', 'auth']):
                return False
            
            # 检查页面标题
            logged_in_title_patterns = ['rewards', 'dashboard', 'account', 'profile']
            logged_out_title_patterns = ['sign in', 'login', 'authenticate']
            
            title_lower = title.lower()
            if any(pattern in title_lower for pattern in logged_in_title_patterns):
                return True
            elif any(pattern in title_lower for pattern in logged_out_title_patterns):
                return False
            
            # 检查页面内容中的关键词
            content_lower = content.lower()
            
            # 登录状态关键词
            logged_in_keywords = [
                'welcome back', 'your account', 'sign out', 'logout',
                'dashboard', 'profile', 'settings', 'your rewards'
            ]
            
            # 登出状态关键词
            logged_out_keywords = [
                'sign in to continue', 'please sign in', 'login required',
                'create account', 'forgot password'
            ]
            
            logged_in_score = sum(1 for keyword in logged_in_keywords 
                                  if keyword in content_lower)
            logged_out_score = sum(1 for keyword in logged_out_keywords 
                                   if keyword in content_lower)
            
            if logged_in_score > logged_out_score and logged_in_score > 0:
                return True
            elif logged_out_score > logged_in_score and logged_out_score > 0:
                return False
            
            return None
            
        except Exception as e:
            logger.debug(f"页面内容检测出错: {e}")
            return None
    
    def _vote_on_status(self, detection_results: Dict[str, Optional[bool]]) -> bool:
        """
        基于多数投票决定登录状态
        
        Args:
            detection_results: 各种检测方法的结果
            
        Returns:
            最终的登录状态
        """
        logged_in_score = 0
        logged_out_score = 0
        
        for method, result in detection_results.items():
            if result is not None:
                weight = self.method_weights.get(method, 1)
                if result:
                    logged_in_score += weight
                else:
                    logged_out_score += weight
        
        logger.debug(f"投票结果 - 登录: {logged_in_score}, 登出: {logged_out_score}")
        logger.info(f"[投票] 登录分数={logged_in_score}, 登出分数={logged_out_score}")
        
        # 如果分数相等，检查 Cookie 检测结果作为决定性因素
        if logged_in_score == logged_out_score:
            cookie_result = detection_results.get('cookie')
            if cookie_result is not None:
                logger.info(f"[投票] 分数平局，使用Cookie检测结果: {cookie_result}")
                return cookie_result
            logger.info(f"[投票] 分数平局且无Cookie结果，默认为未登录")
            return False
        
        return logged_in_score > logged_out_score
    
    def clear_cache(self):
        """清除登录状态缓存"""
        self.cache.clear_cache()
        logger.debug("登录状态缓存已清除")
    
    async def force_recheck(self, page: Page) -> bool:
        """
        强制重新检查登录状态（不使用缓存）
        
        Args:
            page: Playwright页面对象
            
        Returns:
            登录状态
        """
        self.clear_cache()
        return await self.detect_login_status(page, use_cache=False)
    
    def get_detection_info(self) -> Dict[str, Any]:
        """
        获取检测信息（用于调试）
        
        Returns:
            检测信息字典
        """
        return {
            "cache_status": self.cache.cached_status,
            "cache_timestamp": self.cache.cache_timestamp,
            "cache_reason": self.cache.cache_reason,
            "cache_valid": self.cache.get_cached_status() is not None,
        }