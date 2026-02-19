"""
测试任务识别脚本
验证task_parser能否正确识别earn页面的任务
"""

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

project_root = Path(__file__).parent.parent


def get_storage_state_path() -> str | None:
    """Get storage_state path from config or default"""
    try:
        import yaml

        config_path = project_root / "config.yaml"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return config.get("account", {}).get("storage_state_path", "storage_state.json")
    except Exception:
        pass
    return "storage_state.json"


async def test_task_recognition():
    print("=" * 60)
    print("任务识别测试")
    print("=" * 60)

    storage_state = get_storage_state_path()
    storage_state_path = project_root / storage_state if storage_state else None
    has_session = storage_state_path and storage_state_path.exists()

    async with async_playwright() as p:
        print("\n[0] 启动浏览器...")
        use_headless = has_session
        if not use_headless:
            print("  未找到会话状态，使用有头模式以便手动登录")

        browser = await p.chromium.launch(headless=use_headless)

        if has_session:
            context = await browser.new_context(storage_state=str(storage_state_path))
            print("  ✓ 使用已保存的会话状态")
        else:
            context = await browser.new_context()
            print("  ⚠ 未找到会话状态，使用新会话（请手动登录）")

        page = await context.new_page()

        print("\n[1] 导航到earn页面...")
        await page.goto("https://rewards.bing.com/earn", wait_until="domcontentloaded")

        if not has_session:
            print("\n" + "=" * 50)
            print("请在浏览器中完成登录")
            print("登录成功后会自动继续...")
            print("=" * 50)

            for _ in range(60):
                await asyncio.sleep(1)
                pages = context.pages
                if pages:
                    current_page = pages[-1]
                    url = current_page.url
                    if "rewards.bing.com" in url and "login" not in url.lower():
                        print(f"\n检测到登录成功: {url}")
                        page = current_page
                        break
            else:
                print("超时，请手动确认后按Enter继续...")
                input()
                pages = context.pages
                if pages:
                    page = pages[-1]
        else:
            await asyncio.sleep(3)
            if "login" in page.url.lower():
                print("  ⚠ 会话已过期，需要重新登录")
            else:
                print("  ✓ 会话有效，跳过登录等待")

        if "rewards.bing.com/earn" not in page.url:
            print("\n[2] 导航到earn页面...")
            await page.goto("https://rewards.bing.com/earn", wait_until="networkidle")
            await asyncio.sleep(3)

        print(f"\n当前URL: {page.url}")

        print("\n[3] 测试task_parser解析...")
        from tasks.task_parser import TaskParser

        parser = TaskParser()
        tasks = await parser.discover_tasks(page)

        print(f"\n发现 {len(tasks)} 个任务:")
        print("-" * 50)

        completed_count = 0
        incomplete_count = 0
        total_points = 0

        for i, task in enumerate(tasks):
            status = "✅ 已完成" if task.is_completed else "⭕ 未完成"
            print(f"\n[{i + 1}] {task.title}")
            print(f"    类型: {task.task_type} | 积分: {task.points} | {status}")
            print(f"    URL: {task.destination_url[:60]}...")

            if task.is_completed:
                completed_count += 1
            else:
                incomplete_count += 1
            total_points += task.points

        print("\n" + "=" * 50)
        print("统计:")
        print(f"  总任务数: {len(tasks)}")
        print(f"  已完成: {completed_count}")
        print(f"  未完成: {incomplete_count}")
        print(f"  总积分: {total_points}")
        print("=" * 50)

        output_path = Path("logs/diagnostics/task_recognition_test.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "total_tasks": len(tasks),
                    "completed": completed_count,
                    "incomplete": incomplete_count,
                    "total_points": total_points,
                    "tasks": [
                        {
                            "title": t.title,
                            "type": t.task_type,
                            "points": t.points,
                            "completed": t.is_completed,
                            "url": t.destination_url,
                        }
                        for t in tasks
                    ],
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"\n结果已保存到: {output_path}")

        await browser.close()
        print("\n完成！")


if __name__ == "__main__":
    asyncio.run(test_task_recognition())
