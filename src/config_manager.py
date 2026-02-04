"""
配置管理器模块
负责加载、验证和提供配置参数
"""

import os
import logging
from pathlib import Path
from typing import Any, Optional, Dict
import yaml


logger = logging.getLogger(__name__)


# 默认配置
DEFAULT_CONFIG = {
    "search": {
        "desktop_count": 30,
        "mobile_count": 20,
        "wait_interval": {
            "min": 5,
            "max": 15
        },
        "search_terms_file": "tools/search_terms.txt"
    },
    "browser": {
        "headless": False,
        "slow_mo": 100,
        "timeout": 30000
    },
    "account": {
        "storage_state_path": "storage_state.json",
        "login_url": "https://rewards.microsoft.com/"
    },
    "anti_detection": {
        "use_stealth": True,
        "random_viewport": True,
        "simulate_human_typing": True,
        "scroll_behavior": {
            "enabled": True,
            "min_scrolls": 2,
            "max_scrolls": 5,
            "scroll_delay_min": 500,
            "scroll_delay_max": 2000
        }
    },
    "monitoring": {
        "enabled": True,
        "check_points_before_task": True,
        "alert_on_no_increase": True,
        "max_no_increase_count": 3
    },
    "logging": {
        "level": "INFO",
        "file": "logs/automator.log",
        "console": True
    }
}


class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
            self.config = DEFAULT_CONFIG.copy()
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
            
            if loaded_config is None:
                logger.warning("配置文件为空，使用默认配置")
                self.config = DEFAULT_CONFIG.copy()
                return
            
            # 合并加载的配置和默认配置
            self.config = self._merge_configs(DEFAULT_CONFIG, loaded_config)
            logger.info(f"配置文件加载成功: {self.config_path}")
            
        except yaml.YAMLError as e:
            logger.error(f"配置文件解析失败: {e}")
            logger.warning("使用默认配置")
            self.config = DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"加载配置文件时出错: {e}")
            logger.warning("使用默认配置")
            self.config = DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """
        递归合并配置字典
        
        Args:
            default: 默认配置
            loaded: 加载的配置
            
        Returns:
            合并后的配置
        """
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件，返回配置字典
        
        Returns:
            配置字典
        """
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项，支持嵌套键（如 'search.desktop_count'）
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def validate_config(self) -> bool:
        """
        验证配置文件的完整性和有效性
        
        Returns:
            配置是否有效
        """
        required_keys = [
            "search.desktop_count",
            "search.mobile_count",
            "search.wait_interval.min",
            "search.wait_interval.max",
            "browser.headless",
            "account.storage_state_path",
            "logging.level"
        ]
        
        for key in required_keys:
            value = self.get(key)
            if value is None:
                logger.error(f"缺少必需的配置项: {key}")
                return False
        
        # 验证数值范围
        desktop_count = self.get("search.desktop_count")
        if not isinstance(desktop_count, int) or desktop_count < 1:
            logger.error(f"search.desktop_count 必须是正整数: {desktop_count}")
            return False
        
        mobile_count = self.get("search.mobile_count")
        if not isinstance(mobile_count, int) or mobile_count < 1:
            logger.error(f"search.mobile_count 必须是正整数: {mobile_count}")
            return False
        
        wait_min = self.get("search.wait_interval.min")
        wait_max = self.get("search.wait_interval.max")
        if not isinstance(wait_min, (int, float)) or not isinstance(wait_max, (int, float)):
            logger.error("wait_interval 必须是数字")
            return False
        
        if wait_min >= wait_max:
            logger.error(f"wait_interval.min ({wait_min}) 必须小于 wait_interval.max ({wait_max})")
            return False
        
        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        log_level = self.get("logging.level")
        if log_level not in valid_log_levels:
            logger.error(f"无效的日志级别: {log_level}，有效值: {valid_log_levels}")
            return False
        
        logger.info("配置验证通过")
        return True
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"ConfigManager(config_path='{self.config_path}')"
