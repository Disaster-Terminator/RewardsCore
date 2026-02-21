"""
诊断目录轮转清理
保留最近的 N 次诊断记录，删除旧记录
"""

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_DIAGNOSIS_FOLDERS = 10


def cleanup_old_diagnoses(logs_dir: Path, max_folders: int = MAX_DIAGNOSIS_FOLDERS):
    """
    清理旧的诊断目录，保留最近的 N 个

    Args:
        logs_dir: logs 目录路径
        max_folders: 最多保留的文件夹数量
    """
    diagnosis_dir = logs_dir / "diagnosis"
    if not diagnosis_dir.exists():
        return

    folders = sorted(diagnosis_dir.iterdir(), reverse=True)

    for old_folder in folders[max_folders:]:
        try:
            shutil.rmtree(old_folder)
            logger.debug(f"已清理旧诊断目录: {old_folder}")
        except Exception as e:
            logger.warning(f"清理诊断目录失败 {old_folder}: {e}")
