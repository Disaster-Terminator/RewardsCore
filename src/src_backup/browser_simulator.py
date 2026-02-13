"""
浏览器模拟器模块
创建和配置不同平台的浏览器实例，集成反检测机制
"""

import logging
import os
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Playwright

logger = logging.getLogger(__name__)


class BrowserSimulator:
    """浏览器模拟器类"""
    
    def __init__(self, config, anti_ban):
        """
        初始化浏览器模拟器
        
        Args:
            config: ConfigManager 实例
            anti_ban: AntiBanModule 实例
        """
        self.config = config
        self.anti_ban = anti_ban
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        
        logger.info("浏览器模拟器初始化完成")
    
    async def start_playwright(self):
        """启动 Playwright"""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
            logger.info("Playwright 已启动")
    
    async def create_desktop_browser(self, browser_type: str = "edge") -> Browser:
        """
        创建桌面浏览器实例（Edge 或 Chrome）
        
        Args:
            browser_type: 浏览器类型 ("edge" 或 "chrome")
            
        Returns:
            Browser 实例
        """
        await self.start_playwright()
        
        # 获取浏览器配置
        headless = self.config.get("browser.headless", False)
        slow_mo = self.config.get("browser.slow_mo", 100)
        
        # 根据浏览器类型选择设备配置
        device_key = f"desktop_{browser_type}"
        device_config = self.anti_ban.get_device_config(device_key)
        
        logger.info(f"创建桌面浏览器: {browser_type}, headless={headless}")
        
        # 启动 Chromium（Edge 和 Chrome 都使用 Chromium）
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            slow_mo=slow_mo,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-default-browser-check',            # 不检查默认浏览器
                '--disable-default-apps',                # 禁用默认应用
                '--no-first-run',                        # 跳过首次运行
                '--disable-popup-blocking',              # 禁用弹窗阻止
                '--disable-background-timer-throttling', # 禁用后台定时器限制
                '--force-dark-mode',                     # 强制黑夜模式
                '--enable-features=WebUIDarkMode',       # 启用 WebUI 黑夜模式
                '--disable-focus-on-load',               # 禁用加载时自动聚焦
                '--disable-raise-on-focus',              # 禁用聚焦时窗口置顶
                '--no-startup-window',                   # 不显示启动窗口
                '--disable-background-mode',             # 禁用后台模式
                '--disable-backgrounding-occluded-windows', # 禁用被遮挡窗口的后台处理
                '--disable-renderer-backgrounding',      # 禁用渲染器后台处理
                '--disable-features=TranslateUI',        # 禁用翻译UI
                '--disable-ipc-flooding-protection',     # 禁用IPC洪水保护
                '--disable-hang-monitor',                # 禁用挂起监控
                '--disable-prompt-on-repost',            # 禁用重新提交提示
                '--disable-domain-reliability',          # 禁用域可靠性
                '--disable-component-extensions-with-background-pages', # 禁用后台页面组件扩展
            ]
        )
        
        logger.info(f"桌面浏览器创建成功: {browser_type}")
        return self.browser
    
    async def create_mobile_browser(self, device: str = "iPhone 12") -> Browser:
        """
        创建移动设备浏览器实例
        
        Args:
            device: 设备类型 ("iPhone 12" 或 "Android")
            
        Returns:
            Browser 实例
        """
        await self.start_playwright()
        
        # 获取浏览器配置
        headless = self.config.get("browser.headless", False)
        slow_mo = self.config.get("browser.slow_mo", 100)
        
        # 根据设备类型选择配置
        if "iphone" in device.lower():
            device_key = "mobile_iphone"
        else:
            device_key = "mobile_android"
        
        device_config = self.anti_ban.get_device_config(device_key)
        
        logger.info(f"创建移动浏览器: {device}, headless={headless}")
        
        # 启动 Chromium
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            slow_mo=slow_mo,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--no-default-browser-check',
                '--disable-default-apps',
                '--no-first-run',
                '--disable-popup-blocking',              # 禁用弹窗阻止
                '--disable-background-timer-throttling', # 禁用后台定时器限制
                '--force-dark-mode',                     # 强制黑夜模式
                '--enable-features=WebUIDarkMode',       # 启用 WebUI 黑夜模式
                '--disable-focus-on-load',               # 禁用加载时自动聚焦
                '--disable-raise-on-focus',              # 禁用聚焦时窗口置顶
                '--no-startup-window',                   # 不显示启动窗口
                '--disable-background-mode',             # 禁用后台模式
                '--disable-backgrounding-occluded-windows', # 禁用被遮挡窗口的后台处理
                '--disable-renderer-backgrounding',      # 禁用渲染器后台处理
                '--disable-features=TranslateUI',        # 禁用翻译UI
                '--disable-ipc-flooding-protection',     # 禁用IPC洪水保护
                '--disable-hang-monitor',                # 禁用挂起监控
                '--disable-prompt-on-repost',            # 禁用重新提交提示
                '--disable-domain-reliability',          # 禁用域可靠性
                '--disable-component-extensions-with-background-pages', # 禁用后台页面组件扩展
            ]
        )
        
        logger.info(f"移动浏览器创建成功: {device}")
        return self.browser
    
    async def create_context(
        self,
        browser: Browser,
        device_type: str = "desktop_edge",
        storage_state: Optional[str] = None
    ) -> BrowserContext:
        """
        创建浏览器上下文，加载会话状态
        
        Args:
            browser: Browser 实例
            device_type: 设备类型
            storage_state: 会话状态文件路径
            
        Returns:
            BrowserContext 实例
        """
        # 获取设备配置
        device_config = self.anti_ban.get_device_config(device_type)
        
        # 调整视口大小（避免太大）
        viewport = device_config["viewport"].copy()
        if not device_config.get("is_mobile", False):
            # 桌面端使用更合理的窗口大小
            viewport = {"width": 1280, "height": 720}
        
        # 准备上下文选项
        context_options = {
            "user_agent": device_config["user_agent"],
            "viewport": viewport,
            "device_scale_factor": 1.0,  # 固定为 1.0 避免缩放问题
            "is_mobile": device_config.get("is_mobile", False),
            "has_touch": device_config.get("has_touch", False),
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "color_scheme": "dark",  # 设置为黑夜模式
        }
        
        # 如果提供了 storage_state，加载它
        if storage_state and os.path.exists(storage_state):
            context_options["storage_state"] = storage_state
            logger.info(f"加载会话状态: {storage_state}")
        
        # 创建上下文
        context = await browser.new_context(**context_options)
        
        # 为所有新页面添加防置顶脚本
        await context.add_init_script("""
            // 禁用所有可能导致窗口置顶的事件
            window.focus = () => {};
            window.blur = () => {};
            
            // 重写 document.hasFocus 方法
            Object.defineProperty(document, 'hasFocus', {
                value: () => false,
                writable: false
            });
            
            // 禁用焦点相关事件
            ['focus', 'blur', 'focusin', 'focusout'].forEach(eventType => {
                window.addEventListener(eventType, (e) => {
                    e.stopPropagation();
                    e.preventDefault();
                }, true);
            });
            
            // 禁用页面可见性变化事件
            Object.defineProperty(document, 'visibilityState', {
                value: 'hidden',
                writable: false
            });
            
            Object.defineProperty(document, 'hidden', {
                value: true,
                writable: false
            });
        """)
        
        # 应用反检测脚本
        await self.apply_stealth(context)
        
        logger.info(f"浏览器上下文创建成功: {device_type}, 视口: {viewport}")
        return context
    
    async def apply_stealth(self, context: BrowserContext) -> None:
        """
        应用反检测脚本到浏览器上下文
        
        Args:
            context: BrowserContext 实例
        """
        use_stealth = self.config.get("anti_detection.use_stealth", True)
        
        if not use_stealth:
            logger.info("反检测功能已禁用")
            return
        
        logger.info("开始应用反检测脚本...")
        
        # 方法 1: 尝试使用 playwright-stealth（如果可用）
        try:
            from playwright_stealth import stealth_async
            
            # 为上下文中的所有新页面应用 stealth
            async def apply_stealth_to_page(page):
                try:
                    # 检查页面是否已关闭
                    if page.is_closed():
                        logger.debug("页面已关闭，跳过 stealth 应用")
                        return
                    
                    await stealth_async(page)
                    logger.debug("playwright-stealth 应用成功")
                except Exception as e:
                    # 忽略页面已关闭的错误
                    if "closed" in str(e).lower():
                        logger.debug(f"页面已关闭，跳过 stealth: {e}")
                    else:
                        logger.warning(f"应用 stealth 失败: {e}")
            
            # 监听新页面创建事件
            context.on("page", lambda page: apply_stealth_to_page(page))
            
            logger.info("使用 playwright-stealth 库")
            
        except ImportError:
            logger.warning("playwright-stealth 未安装，使用原生方法")
        
        # 方法 2: 使用原生 add_init_script 方法（备用或补充）
        scripts = self.anti_ban.get_stealth_scripts()
        
        for script in scripts:
            try:
                await context.add_init_script(script)
            except Exception as e:
                logger.warning(f"注入脚本失败: {e}")
        
        logger.info("反检测脚本应用完成")
    
    async def create_manual_login_context(
        self,
        device_type: str = "desktop_edge"
    ) -> tuple[Browser, BrowserContext]:
        """
        创建用于手动登录的浏览器上下文
        这个方法会以有头模式启动浏览器，方便用户手动登录
        
        Args:
            device_type: 设备类型
            
        Returns:
            (Browser, BrowserContext) 元组
        """
        logger.info("=== 手动登录模式 ===")
        logger.info("浏览器将以有头模式启动，请手动完成登录")
        
        # 强制使用有头模式
        original_headless = self.config.get("browser.headless")
        self.config.config["browser"]["headless"] = False
        
        # 创建浏览器
        if "mobile" in device_type:
            browser = await self.create_mobile_browser()
        else:
            browser_type = device_type.split("_")[1] if "_" in device_type else "edge"
            browser = await self.create_desktop_browser(browser_type)
        
        # 创建上下文（不加载 storage_state）
        context = await self.create_context(browser, device_type, storage_state=None)
        
        # 恢复原始配置
        self.config.config["browser"]["headless"] = original_headless
        
        logger.info("手动登录浏览器已启动")
        return browser, context
    
    async def close_browser(self):
        """只关闭浏览器，不停止 Playwright"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            logger.info("浏览器已关闭")
    
    async def close(self):
        """关闭浏览器和 Playwright"""
        await self.close_browser()
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            logger.info("Playwright 已停止")
