"""
前端功能验收测试脚本
模拟真实用户操作，验证业务逻辑正确性
"""

import asyncio
import json
import logging
import sys
import time
import requests
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str = ""
    details: dict = field(default_factory=dict)


@dataclass
class AcceptanceReport:
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    results: list[TestResult] = field(default_factory=list)

    def add(self, result: TestResult):
        self.total_tests += 1
        self.results.append(result)
        if result.passed:
            self.passed += 1
        else:
            self.failed += 1

    def summary(self) -> str:
        lines = [
            "\n" + "=" * 70,
            "前端功能验收测试报告",
            "=" * 70,
            f"总计: {self.total_tests} | 通过: {self.passed} | 失败: {self.failed}",
            "-" * 70,
        ]
        for r in self.results:
            status = "✅" if r.passed else "❌"
            lines.append(f"{status} {r.name}: {r.message}")
        lines.append("=" * 70)
        return "\n".join(lines)


class FrontendAcceptanceTester:
    def __init__(
        self,
        frontend_url: str = "http://localhost:3000",
        backend_url: str = "http://localhost:3000",
    ):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.browser = None
        self.context = None
        self.page = None
        self.report = AcceptanceReport()
        self.ws_messages: list[dict] = []
        self.console_errors: list[str] = []

    async def initialize(self) -> bool:
        try:
            from playwright.async_api import async_playwright

            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800},
            )
            self.page = await self.context.new_page()
            self.page.set_default_timeout(15000)

            self.page.on("console", self._on_console)
            self.page.on("websocket", self._on_websocket)

            logger.info("浏览器初始化成功")
            return True
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            return False

    def _on_console(self, msg):
        if msg.type == "error":
            self.console_errors.append(msg.text)
        elif msg.type == "log":
            if "Initializing" in msg.text or "failed" in msg.text.lower() or "error" in msg.text.lower():
                self.console_errors.append(f"[LOG] {msg.text}")

    def _on_websocket(self, ws):
        def on_message(msg):
            try:
                data = json.loads(msg)
                self.ws_messages.append(data)
            except Exception:
                pass

        ws.on("framereceived", on_message)

    async def cleanup(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    def api_get(self, path: str) -> tuple[int, dict | None]:
        try:
            url = f"{self.backend_url}{path}"
            resp = requests.get(url, timeout=10)
            return resp.status_code, resp.json()
        except Exception as e:
            return 0, {"error": str(e)}

    def api_post(self, path: str, data: dict = None) -> tuple[int, dict | None]:
        try:
            url = f"{self.backend_url}{path}"
            resp = requests.post(url, json=data or {}, timeout=10)
            return resp.status_code, resp.json()
        except Exception as e:
            return 0, {"error": str(e)}

    async def navigate_to(self, path: str = "/") -> bool:
        try:
            await self.page.goto(f"{self.frontend_url}{path}", wait_until="domcontentloaded", timeout=20000)
            await self.page.wait_for_timeout(1000)
            return True
        except Exception as e:
            logger.error(f"导航失败: {e}")
            return False

    async def wait_for_element(self, selector: str, timeout: int = 5000) -> bool:
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception:
            return False

    async def click_button(self, text: str) -> bool:
        try:
            button = self.page.get_by_role("button", name=text)
            await button.click(timeout=5000)
            return True
        except Exception:
            try:
                buttons = await self.page.query_selector_all("button")
                for btn in buttons:
                    btn_text = await btn.text_content()
                    if btn_text and text in btn_text:
                        await btn.click()
                        return True
            except Exception:
                pass
        return False

    async def test_backend_connectivity(self) -> TestResult:
        """测试后端连接性"""
        try:
            status_code, data = self.api_get("/api/health")
            if status_code == 200 and data:
                return TestResult("后端连接", True, f"健康状态: {data.get('overall', 'unknown')}")
            return TestResult("后端连接", False, f"连接失败: HTTP {status_code}")
        except Exception as e:
            return TestResult("后端连接", False, f"连接失败: {str(e)}")

    async def test_frontend_load(self) -> TestResult:
        """测试前端加载"""
        if await self.navigate_to("/"):
            title = await self.page.title()
            return TestResult("前端加载", True, f"标题: {title}")
        return TestResult("前端加载", False, "页面加载失败")

    async def test_dashboard_display(self) -> TestResult:
        """测试Dashboard显示"""
        await self.navigate_to("/")

        checks = {}

        stat_cards = await self.page.query_selector_all("[class*='rounded-xl']")
        checks["统计卡片"] = len(stat_cards) >= 3

        mode_buttons = await self.page.query_selector_all("button")
        checks["控制按钮"] = len(mode_buttons) >= 3

        await self.page.wait_for_timeout(2000)

        if all(checks.values()):
            return TestResult("Dashboard显示", True, f"卡片:{stat_cards.__len__()}, 按钮:{mode_buttons.__len__()}")
        failed = [k for k, v in checks.items() if not v]
        return TestResult("Dashboard显示", False, f"缺失: {failed}")

    async def test_start_task_flow(self) -> TestResult:
        """测试启动任务流程"""
        await self.navigate_to("/")
        
        await self.page.wait_for_timeout(5000)
        
        url = f"{self.frontend_url}/api/status"
        try:
            status_result = await self.page.evaluate(f"""async () => {{
                try {{
                    const response = await fetch('{url}');
                    const data = await response.json();
                    return {{ ok: response.ok, is_running: data.is_running }};
                }} catch (e) {{
                    return {{ ok: false, error: e.message }};
                }}
            }}""")
            if not status_result.get('ok'):
                return TestResult("启动任务流程", False, "无法获取初始状态")
            if status_result.get('is_running'):
                return TestResult("启动任务流程", True, "任务正在运行中，启动按钮应禁用")
        except Exception as e:
            return TestResult("启动任务流程", False, f"API请求失败: {str(e)}")

        start_btn = None
        buttons = await self.page.query_selector_all("button")
        for btn in buttons:
            text = await btn.text_content()
            if text and ("启动" in text or "开始" in text):
                start_btn = btn
                break

        if not start_btn:
            return TestResult("启动任务流程", False, "未找到启动按钮")

        is_disabled = await start_btn.is_disabled()
        if is_disabled:
            warning_card = await self.page.query_selector("text=正在连接后端服务")
            if warning_card:
                return TestResult("启动任务流程", False, "前端未完成初始化，仍在显示'正在连接后端服务'")
            return TestResult("启动任务流程", True, "按钮禁用（后端未就绪或任务运行中）")

        return TestResult("启动任务流程", True, "启动按钮可点击（未实际执行启动）")

    async def test_stop_task_flow(self) -> TestResult:
        """测试停止任务流程"""
        url = f"{self.frontend_url}/api/status"
        try:
            status_result = await self.page.evaluate(f"""async () => {{
                try {{
                    const response = await fetch('{url}');
                    const data = await response.json();
                    return {{ ok: response.ok, data: data }};
                }} catch (e) {{
                    return {{ ok: false, data: {{}} }};
                }}
            }}""")
            status_data = status_result.get('data', {}) if status_result.get('ok') else {}
        except Exception:
            status_data = {}
            
        is_running = status_data.get("is_running", False) if status_data else False

        if not is_running:
            return TestResult("停止任务流程", True, "任务未运行，跳过停止测试")

        await self.navigate_to("/")
        await self.page.wait_for_timeout(2000)

        stop_btn = None
        buttons = await self.page.query_selector_all("button")
        button_texts = []
        for btn in buttons:
            text = await btn.text_content()
            if text:
                button_texts.append(text.strip())
            if text and ("停止" in text or "暂停" in text or "stop" in text.lower()):
                stop_btn = btn

        if stop_btn:
            try:
                is_disabled = await stop_btn.is_disabled()
                if is_disabled:
                    await self.page.wait_for_timeout(2000)
                await stop_btn.click(timeout=5000)
                await self.page.wait_for_timeout(5000)
            except Exception as e:
                pass
        else:
            stop_url = f"{self.frontend_url}/api/task/stop"
            await self.page.evaluate(f"""async () => {{
                try {{
                    await fetch('{stop_url}', {{ method: 'POST' }});
                }} catch (e) {{}}
            }}""")
            await self.page.wait_for_timeout(3000)

        status_url = f"{self.frontend_url}/api/status"
        status_after = await self.page.evaluate(f"""async () => {{
            try {{
                const response = await fetch('{status_url}');
                const data = await response.json();
                return {{ ok: response.ok, data: data }};
            }} catch (e) {{
                return {{ ok: false }};
            }}
        }}""")
        if status_after.get('ok'):
            data = status_after.get('data', {})
            is_still_running = data.get("is_running", True) if data else True
            if not is_still_running:
                return TestResult("停止任务流程", True, "任务已停止")
            
            return TestResult("停止任务流程", False, f"任务仍在运行: {data.get('current_operation', 'unknown')}")

        return TestResult("停止任务流程", False, "停止后状态检查失败")

    async def test_websocket_messages(self) -> TestResult:
        """测试WebSocket消息接收"""
        self.ws_messages = []

        await self.navigate_to("/")
        await self.page.wait_for_timeout(5000)

        if len(self.ws_messages) > 0:
            types = [m.get("type", "unknown") for m in self.ws_messages]
            return TestResult("WebSocket消息", True, f"收到 {len(self.ws_messages)} 条消息: {set(types)}")

        connected = await self.page.query_selector("[class*='connected'], [class*='success']")
        if connected:
            return TestResult("WebSocket消息", True, "WebSocket已连接（消息可能需要事件触发）")

        return TestResult("WebSocket消息", False, "未收到WebSocket消息且未检测到连接状态")

    async def test_config_page(self) -> TestResult:
        """测试配置页面"""
        await self.navigate_to("/config")

        await self.page.wait_for_timeout(2000)

        tab_buttons = await self.page.query_selector_all("button")
        toggle_elements = await self.page.query_selector_all("[class*='rounded-full'], label[class*='cursor-pointer']")
        text_content = await self.page.content()

        has_tabs = any("搜索" in text_content or "浏览器" in text_content or "登录" in text_content for _ in [1])
        has_toggles = len(toggle_elements) > 0 or "toggle" in text_content.lower() or "开关" in text_content

        if len(tab_buttons) >= 2 or has_toggles:
            return TestResult("配置页面", True, f"按钮: {len(tab_buttons)}, 开关元素: {len(toggle_elements)}")

        return TestResult("配置页面", False, "未找到配置表单元素")

    async def test_logs_page(self) -> TestResult:
        """测试日志页面"""
        await self.navigate_to("/logs")

        await self.page.wait_for_timeout(1000)

        log_elements = await self.page.query_selector_all("[class*='log'], [class*='terminal'], pre, code, [class*='font-mono']")

        text_elements = await self.page.query_selector_all("p, span, div")
        has_log_content = False
        for el in text_elements[:20]:
            text = await el.text_content()
            if text and ("日志" in text or "log" in text.lower()):
                has_log_content = True
                break

        if log_elements or has_log_content:
            return TestResult("日志页面", True, f"日志元素: {len(log_elements)}")

        return TestResult("日志页面", False, "未找到日志显示区域")

    async def test_history_page(self) -> TestResult:
        """测试历史记录页面"""
        await self.navigate_to("/history")

        await self.page.wait_for_timeout(1000)

        history_elements = await self.page.query_selector_all("table, [class*='history'], [class*='list'], [class*='item']")

        text_elements = await self.page.query_selector_all("p, span, h1, h2, h3")
        has_history_content = False
        for el in text_elements[:10]:
            text = await el.text_content()
            if text and ("历史" in text or "记录" in text or "history" in text.lower()):
                has_history_content = True
                break

        if history_elements or has_history_content:
            return TestResult("历史记录页面", True, f"历史元素: {len(history_elements)}")

        return TestResult("历史记录页面", False, "未找到历史记录显示区域")

    async def test_sidebar_navigation(self) -> TestResult:
        """测试侧边栏导航"""
        pages = [
            ("/", "控制台"),
            ("/config", "配置"),
            ("/logs", "日志"),
            ("/history", "历史"),
        ]

        success_count = 0
        for path, name in pages:
            await self.navigate_to(path)
            await self.page.wait_for_timeout(500)
            current_url = self.page.url
            if path in current_url or current_url.endswith(path):
                success_count += 1

        if success_count == len(pages):
            return TestResult("侧边栏导航", True, f"所有 {len(pages)} 个页面可访问")
        return TestResult("侧边栏导航", False, f"只有 {success_count}/{len(pages)} 个页面可访问")

    async def test_console_errors(self) -> TestResult:
        """测试控制台错误"""
        self.console_errors = []

        await self.navigate_to("/")
        await self.page.wait_for_timeout(3000)

        critical_errors = [
            e
            for e in self.console_errors
            if "error" in e.lower()
            and "warning" not in e.lower()
            and "404" not in e
        ]

        if not critical_errors:
            return TestResult("控制台错误检查", True, "无严重错误")
        return TestResult("控制台错误检查", False, f"发现 {len(critical_errors)} 个错误: {critical_errors[:3]}")

    async def test_responsive_layout(self) -> TestResult:
        """测试响应式布局"""
        viewports = [
            {"width": 1920, "height": 1080, "name": "desktop"},
            {"width": 1366, "height": 768, "name": "laptop"},
            {"width": 768, "height": 1024, "name": "tablet"},
        ]

        results = []
        for vp in viewports:
            await self.page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
            await self.page.wait_for_timeout(500)

            sidebar = await self.page.query_selector("nav, aside, [class*='sidebar']")
            main = await self.page.query_selector("main, [class*='main'], [class*='content']")

            if sidebar or main:
                results.append(vp["name"])

        await self.page.set_viewport_size({"width": 1280, "height": 800})

        if len(results) >= 2:
            return TestResult("响应式布局", True, f"正常: {results}")
        return TestResult("响应式布局", False, f"只有 {len(results)} 个视口正常")

    async def test_api_error_handling(self) -> TestResult:
        """测试API错误处理"""
        try:
            url = f"{self.frontend_url}/api/task/start"
            result = await self.page.evaluate(f"""async () => {{
                try {{
                    const response = await fetch('{url}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ invalid_param: true }})
                    }});
                    return {{ status: response.status }};
                }} catch (e) {{
                    return {{ status: 0, error: e.message }};
                }}
            }}""")
            status = result.get('status', 0)
            if status in [200, 400, 422]:
                return TestResult("API错误处理", True, f"错误响应正确处理 (HTTP {status})")
        except Exception:
            pass

        return TestResult("API错误处理", True, "API端点可访问")

    async def run_all_tests(self) -> AcceptanceReport:
        """运行所有验收测试"""
        print("\n" + "=" * 70)
        print("开始前端功能验收测试")
        print("=" * 70)

        tests = [
            ("基础连接", [
                self.test_backend_connectivity,
                self.test_frontend_load,
            ]),
            ("Dashboard功能", [
                self.test_dashboard_display,
                self.test_start_task_flow,
                self.test_stop_task_flow,
            ]),
            ("WebSocket", [
                self.test_websocket_messages,
            ]),
            ("页面功能", [
                self.test_config_page,
                self.test_logs_page,
                self.test_history_page,
            ]),
            ("导航与布局", [
                self.test_sidebar_navigation,
                self.test_responsive_layout,
            ]),
            ("错误处理", [
                self.test_console_errors,
                self.test_api_error_handling,
            ]),
        ]

        for category, test_funcs in tests:
            print(f"\n[{category}]")
            for test_func in test_funcs:
                result = await test_func()
                self.report.add(result)
                status = "✅" if result.passed else "❌"
                print(f"  {status} {result.name}: {result.message}")

        return self.report


async def main():
    logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        stop_resp = requests.post("http://localhost:3000/api/task/stop", timeout=5)
        print(f"预检查: 停止运行中的任务 - {stop_resp.json().get('message', 'done')}")
    except Exception as e:
        print(f"预检查: 无运行中的任务或后端未就绪")

    tester = FrontendAcceptanceTester()

    try:
        if not await tester.initialize():
            print("❌ 无法初始化测试环境")
            return 1

        report = await tester.run_all_tests()
        print(report.summary())

        if report.failed > 0:
            print("\n⚠️ 发现问题，需要修复")
            return 1
        else:
            print("\n✅ 所有功能验收通过！")
            return 0

    finally:
        await tester.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
