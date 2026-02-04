"""
MS Rewards Automator - 主程序入口
支持命令行参数和调度模式
"""

import asyncio
import sys
import os
import signal
import argparse
from pathlib import Path
from datetime import datetime

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config_manager import ConfigManager
from logger import setup_logging
from anti_ban_module import AntiBanModule
from browser_simulator import BrowserSimulator
from search_term_generator import SearchTermGenerator
from search_engine import SearchEngine
from points_detector import PointsDetector
from account_manager import AccountManager
from state_monitor import StateMonitor
from error_handler import ErrorHandler
from notificator import Notificator
from scheduler import TaskScheduler

import logging

logger = None
browser_sim = None
notificator = None


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="MS Rewards Automator - 自动化完成 Microsoft Rewards 任务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                          # 立即执行一次任务
  python main.py --headless               # 无头模式执行
  python main.py --mode fast              # 快速模式（减少等待时间）
  python main.py --schedule               # 调度模式（每天自动执行）
  python main.py --schedule --schedule-now # 调度模式（立即执行一次后进入调度）
  python main.py --desktop-only           # 仅执行桌面搜索
  python main.py --mobile-only            # 仅执行移动搜索
  python main.py --test-notification      # 测试通知功能
        """
    )
    
    # 执行模式
    parser.add_argument(
        "--mode",
        choices=["normal", "fast", "slow"],
        default="normal",
        help="执行模式: normal(正常), fast(快速), slow(慢速)"
    )
    
    # 浏览器选项
    parser.add_argument(
        "--headless",
        action="store_true",
        help="无头模式（不显示浏览器窗口）"
    )
    
    parser.add_argument(
        "--browser",
        choices=["edge", "chrome"],
        default="edge",
        help="浏览器类型"
    )
    
    # 任务选项
    parser.add_argument(
        "--desktop-only",
        action="store_true",
        help="仅执行桌面搜索任务"
    )
    
    parser.add_argument(
        "--mobile-only",
        action="store_true",
        help="仅执行移动搜索任务"
    )
    
    parser.add_argument(
        "--skip-daily-tasks",
        action="store_true",
        help="跳过日常任务面板"
    )
    
    # 调度选项
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="启用调度模式（常驻后台，每天自动执行）"
    )
    
    parser.add_argument(
        "--schedule-now",
        action="store_true",
        help="调度模式下立即执行一次任务（用于测试）"
    )
    
    # 配置文件
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="配置文件路径"
    )
    
    # 测试选项
    parser.add_argument(
        "--test-notification",
        action="store_true",
        help="测试通知功能"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="模拟运行（不执行实际搜索）"
    )
    
    return parser.parse_args()


async def execute_main_task(args, config):
    """
    执行主任务
    
    Args:
        args: 命令行参数
        config: ConfigManager 实例
    """
    global browser_sim, notificator
    
    # 自动检测登录状态，决定是否使用无头模式
    storage_state_path = config.get("account.storage_state_path", "storage_state.json")
    has_login_state = os.path.exists(storage_state_path)
    
    # 如果没有登录状态且没有明确指定 --headless，自动切换到有头模式
    if not has_login_state and not args.headless:
        logger.info("检测到首次运行（无登录状态），自动切换到有头模式以便登录")
        config.config["browser"]["headless"] = False
    
    # 应用命令行参数到配置
    if args.headless:
        config.config["browser"]["headless"] = True
    
    if args.mode == "fast":
        config.config["search"]["wait_interval"]["min"] = 2
        config.config["search"]["wait_interval"]["max"] = 5
        config.config["browser"]["slow_mo"] = 50
    elif args.mode == "slow":
        config.config["search"]["wait_interval"]["min"] = 15
        config.config["search"]["wait_interval"]["max"] = 30
        config.config["browser"]["slow_mo"] = 200
    
    logger.info("=" * 70)
    logger.info("MS Rewards Automator - 开始执行")
    logger.info("=" * 70)
    logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"执行模式: {args.mode}")
    logger.info(f"浏览器: {args.browser}")
    logger.info(f"无头模式: {config.get('browser.headless', True)}")
    logger.info("=" * 70)
    
    try:
        
        # 初始化组件
        logger.info("\n[1/8] 初始化组件...")
        anti_ban = AntiBanModule(config)
        browser_sim = BrowserSimulator(config, anti_ban)
        term_gen = SearchTermGenerator(config)
        points_det = PointsDetector()
        search_engine = SearchEngine(config, term_gen, anti_ban)
        account_mgr = AccountManager(config)
        state_monitor = StateMonitor(config, points_det)
        error_handler = ErrorHandler(config)
        notificator = Notificator(config)
        logger.info("  ✓ 完成")
        
        # 创建浏览器
        logger.info("\n[2/8] 创建浏览器...")
        browser = await browser_sim.create_desktop_browser(args.browser)
        context = await browser_sim.create_context(
            browser,
            f"desktop_{args.browser}",
            storage_state=config.get("account.storage_state_path")
        )
        page = await context.new_page()
        logger.info("  ✓ 完成")
        
        # 检查登录状态
        logger.info("\n[3/8] 检查登录状态...")
        is_logged_in = await account_mgr.is_logged_in(page)
        
        if not is_logged_in:
            logger.warning("  未登录，需要手动登录")
            logger.info("  请在浏览器中完成登录...")
            await account_mgr.wait_for_manual_login(page)
            await account_mgr.save_session(context)
            logger.info("  ✓ 登录完成，会话已保存")
        else:
            logger.info("  ✓ 已登录")
        
        # 检查初始积分
        logger.info("\n[4/8] 检查初始积分...")
        initial_points = await state_monitor.check_points_before_task(page)
        
        # 执行桌面搜索
        if not args.mobile_only:
            logger.info("\n[5/8] 执行桌面搜索...")
            desktop_count = config.get("search.desktop_count")
            
            if args.dry_run:
                logger.info(f"  [模拟] 将执行 {desktop_count} 次桌面搜索")
            else:
                success = await search_engine.execute_desktop_searches(page, desktop_count)
                
                if success:
                    logger.info(f"  ✓ 桌面搜索完成 ({desktop_count} 次)")
                else:
                    logger.warning("  ⚠ 桌面搜索部分失败")
                
                # 检查积分
                await state_monitor.check_points_after_searches(page, "desktop")
        else:
            logger.info("\n[5/8] 跳过桌面搜索（--mobile-only）")
        
        # 执行移动搜索
        if not args.desktop_only:
            logger.info("\n[6/8] 执行移动搜索...")
            mobile_count = config.get("search.mobile_count")
            
            if args.dry_run:
                logger.info(f"  [模拟] 将执行 {mobile_count} 次移动搜索")
            else:
                # 关闭桌面浏览器（但保持 Playwright 运行）
                await browser_sim.close_browser()
                
                # 创建移动浏览器
                logger.info("  创建移动浏览器...")
                browser = await browser_sim.create_mobile_browser("iphone")
                context = await browser_sim.create_context(
                    browser,
                    "mobile_iphone",
                    storage_state=config.get("account.storage_state_path")
                )
                page = await context.new_page()
                
                success = await search_engine.execute_mobile_searches(page, mobile_count)
                
                if success:
                    logger.info(f"  ✓ 移动搜索完成 ({mobile_count} 次)")
                else:
                    logger.warning("  ⚠ 移动搜索部分失败")
                
                # 检查积分
                await state_monitor.check_points_after_searches(page, "mobile")
        else:
            logger.info("\n[6/8] 跳过移动搜索（--desktop-only）")
        
        # 执行日常任务（暂时跳过，因为 TaskExecutor 未完全实现）
        if not args.skip_daily_tasks:
            logger.info("\n[7/8] 执行日常任务...")
            logger.info("  ⚠ 日常任务功能待实现")
        else:
            logger.info("\n[7/8] 跳过日常任务")
        
        # 生成报告和发送通知
        logger.info("\n[8/8] 生成报告...")
        
        # 保存每日报告
        state_monitor.save_daily_report()
        
        # 获取状态
        state = state_monitor.get_account_state()
        
        # 发送通知
        if notificator.enabled and not args.dry_run:
            logger.info("  发送通知...")
            report_data = {
                "points_gained": state["points_gained"],
                "current_points": state["current_points"],
                "desktop_searches": state["session_data"]["desktop_searches"],
                "mobile_searches": state["session_data"]["mobile_searches"],
                "status": "正常" if state["points_gained"] > 0 else "无积分增加",
                "alerts": state["session_data"]["alerts"]
            }
            
            await notificator.send_daily_report(report_data)
        
        # 显示摘要
        logger.info("\n" + "=" * 70)
        logger.info("执行摘要")
        logger.info("=" * 70)
        logger.info(f"初始积分: {state['initial_points']:,}" if state['initial_points'] else "初始积分: 未知")
        logger.info(f"当前积分: {state['current_points']:,}" if state['current_points'] else "当前积分: 未知")
        logger.info(f"获得积分: +{state['points_gained']}")
        logger.info(f"桌面搜索: {state['session_data']['desktop_searches']} 次")
        logger.info(f"移动搜索: {state['session_data']['mobile_searches']} 次")
        logger.info(f"告警数量: {len(state['session_data']['alerts'])}")
        logger.info("=" * 70)
        
        # 关闭浏览器
        logger.info("\n关闭浏览器...")
        await browser_sim.close()
        logger.info("✓ 完成")
        
        logger.info("\n✅ 任务执行完成")
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠ 用户中断")
        if browser_sim:
            await browser_sim.close()
    except Exception as e:
        logger.error(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        if browser_sim:
            await browser_sim.close()
        raise


async def test_notification_func(config):
    """测试通知功能"""
    logger.info("=" * 70)
    logger.info("测试通知功能")
    logger.info("=" * 70)
    
    notif = Notificator(config)
    
    if not notif.enabled:
        logger.error("通知功能未启用，请检查配置文件")
        return
    
    results = await notif.test_notification()
    
    logger.info("\n测试结果:")
    for channel, success in results.items():
        status = "✓ 成功" if success else "✗ 失败"
        logger.info(f"  {channel}: {status}")
    
    logger.info("=" * 70)


def signal_handler(signum, frame):
    """信号处理器"""
    global browser_sim
    logger.info("\n收到中断信号，正在清理...")
    if browser_sim:
        asyncio.create_task(browser_sim.close())
    sys.exit(0)


async def main():
    """主函数"""
    global logger
    
    # 解析参数
    args = parse_arguments()
    
    # 初始化日志
    log_level = "DEBUG" if args.dry_run else "INFO"
    setup_logging(log_level=log_level, log_file="logs/automator.log", console=True)
    logger = logging.getLogger(__name__)
    
    # 加载配置
    try:
        config = ConfigManager(args.config)
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        sys.exit(1)
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 测试通知
    if args.test_notification:
        await test_notification_func(config)
        return
    
    # 调度模式
    if args.schedule:
        logger.info("启动调度模式...")
        scheduler = TaskScheduler(config)
        
        # 定义调度任务
        async def scheduled_task():
            await execute_main_task(args, config)
        
        # 如果指定了 --schedule-now，立即执行一次
        if args.schedule_now:
            logger.info("\n⚡ 立即执行一次任务（测试模式）...")
            logger.info("=" * 70)
            await scheduled_task()
            logger.info("=" * 70)
            logger.info("✓ 立即执行完成，现在进入正常调度模式\n")
        
        await scheduler.run_scheduled_task(scheduled_task)
    else:
        # 立即执行
        await execute_main_task(args, config)


if __name__ == "__main__":
    asyncio.run(main())
