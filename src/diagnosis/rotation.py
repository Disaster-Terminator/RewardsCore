"""
诊断目录轮转清理
保留最近的 N 次诊断记录，删除旧记录
"""

import logging
import shutil
import time
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_DIAGNOSIS_FOLDERS = 10
MAX_AGE_DAYS = 7


def cleanup_old_diagnoses(
    logs_dir: Path,
    max_folders: int = MAX_DIAGNOSIS_FOLDERS,
    max_age_days: int = MAX_AGE_DAYS,
) -> dict:
    """
    清理旧的诊断目录，保留最近的 N 个

    Args:
        logs_dir: logs 目录路径
        max_folders: 最多保留的文件夹数量
        max_age_days: 最大保留天数

    Returns:
        清理结果统计
    """
    diagnosis_dir = logs_dir / "diagnosis"
    if not diagnosis_dir.exists():
        return {"deleted": 0, "skipped": 0}

    folders = sorted(diagnosis_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)

    result = {"deleted": 0, "skipped": 0, "errors": 0}
    age_threshold = max_age_days * 24 * 60 * 60

    for i, folder in enumerate(folders):
        if not folder.is_dir():
            continue

        try:
            folder_age = time.time() - folder.stat().st_mtime

            if i >= max_folders or folder_age > age_threshold:
                shutil.rmtree(folder)
                logger.debug(f"已清理旧诊断目录: {folder}")
                result["deleted"] += 1
            else:
                result["skipped"] += 1
        except Exception as e:
            logger.warning(f"清理诊断目录失败 {folder}: {e}")
            result["errors"] += 1

    if result["deleted"] > 0:
        logger.info(f"诊断目录清理完成: 删除 {result['deleted']} 个旧目录")

    return result
