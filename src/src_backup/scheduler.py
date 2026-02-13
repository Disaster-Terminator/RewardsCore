"""
任务调度器模块
支持定时执行和随机时间调度
"""

import logging
import asyncio
import random
from datetime import datetime, time, timedelta
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class TaskScheduler:
    """任务调度器类"""
    
    def __init__(self, config):
        """
        初始化任务调度器
        
        Args:
            config: ConfigManager 实例
        """
        self.config = config
        
        # 调度配置
        self.enabled = config.get("scheduler.enabled", False)
        self.mode = config.get("scheduler.mode", "random")  # "random" 或 "fixed"
        
        # 随机模式配置
        self.random_start_hour = config.get("scheduler.random_start_hour", 8)
        self.random_end_hour = config.get("scheduler.random_end_hour", 22)
        
        # 固定模式配置
        self.fixed_hour = config.get("scheduler.fixed_hour", 10)
        self.fixed_minute = config.get("scheduler.fixed_minute", 0)
        
        self.running = False
        self.next_run_time = None
        
        logger.info(f"任务调度器初始化完成 (enabled={self.enabled}, mode={self.mode})")
    
    def calculate_next_run_time(self) -> datetime:
        """
        计算下次运行时间
        
        Returns:
            下次运行的 datetime 对象
        """
        now = datetime.now()
        
        if self.mode == "random":
            # 随机模式：在指定时间范围内随机选择
            target_hour = random.randint(self.random_start_hour, self.random_end_hour)
            target_minute = random.randint(0, 59)
            
            # 计算目标时间
            target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            
            # 如果目标时间已过，设置为明天
            if target_time <= now:
                target_time += timedelta(days=1)
            
            logger.info(f"随机调度: 下次运行时间 {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            # 固定模式：每天固定时间
            target_time = now.replace(
                hour=self.fixed_hour,
                minute=self.fixed_minute,
                second=0,
                microsecond=0
            )
            
            # 如果目标时间已过，设置为明天
            if target_time <= now:
                target_time += timedelta(days=1)
            
            logger.info(f"固定调度: 下次运行时间 {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return target_time
    
    async def wait_until_next_run(self) -> None:
        """等待到下次运行时间"""
        self.next_run_time = self.calculate_next_run_time()
        
        now = datetime.now()
        wait_seconds = (self.next_run_time - now).total_seconds()
        
        logger.info(f"等待 {wait_seconds / 3600:.2f} 小时后执行任务...")
        
        # 分段等待，每小时检查一次
        while wait_seconds > 0:
            sleep_time = min(wait_seconds, 3600)  # 最多等待1小时
            await asyncio.sleep(sleep_time)
            wait_seconds -= sleep_time
            
            if wait_seconds > 0:
                logger.debug(f"还需等待 {wait_seconds / 3600:.2f} 小时...")
    
    async def run_scheduled_task(self, task_func: Callable) -> None:
        """
        运行调度任务
        
        Args:
            task_func: 要执行的任务函数（异步）
        """
        if not self.enabled:
            logger.warning("调度器未启用")
            return
        
        self.running = True
        logger.info("=" * 60)
        logger.info("任务调度器启动")
        logger.info("=" * 60)
        
        try:
            while self.running:
                # 等待到下次运行时间
                await self.wait_until_next_run()
                
                # 执行任务
                logger.info("=" * 60)
                logger.info(f"开始执行定时任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info("=" * 60)
                
                try:
                    await task_func()
                    logger.info("✓ 定时任务执行完成")
                except Exception as e:
                    logger.error(f"❌ 定时任务执行失败: {e}")
                    import traceback
                    traceback.print_exc()
                
                logger.info("=" * 60)
                
        except KeyboardInterrupt:
            logger.info("收到中断信号，停止调度器")
            self.running = False
        except Exception as e:
            logger.error(f"调度器异常: {e}")
            self.running = False
    
    def stop(self) -> None:
        """停止调度器"""
        logger.info("停止任务调度器...")
        self.running = False
    
    def get_status(self) -> dict:
        """
        获取调度器状态
        
        Returns:
            状态字典
        """
        return {
            "enabled": self.enabled,
            "running": self.running,
            "mode": self.mode,
            "next_run_time": self.next_run_time.isoformat() if self.next_run_time else None,
            "config": {
                "random_start_hour": self.random_start_hour,
                "random_end_hour": self.random_end_hour,
                "fixed_hour": self.fixed_hour,
                "fixed_minute": self.fixed_minute
            }
        }
