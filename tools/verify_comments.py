#!/usr/bin/env python3
"""比较数据库和 GitHub API 的数据"""

import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from review.comment_manager import ReviewManager
from review.graphql_client import GraphQLClient
from review.models import ReviewThreadState


def load_env_file() -> None:
    """从 .env 文件加载环境变量"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value and key not in os.environ:
                        os.environ[key] = value


def load_db_data() -> list[ReviewThreadState]:
    """从数据库加载数据（使用 ReviewManager 确保并发安全）"""
    manager = ReviewManager()
    return manager.get_all_threads()


def fetch_api_data() -> list[dict[str, Any]]:
    """从 GitHub API 获取数据"""
    load_env_file()
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("错误: 缺少 GITHUB_TOKEN 环境变量")
        sys.exit(1)

    client = GraphQLClient(token)
    return client.fetch_pr_threads("Disaster-Terminator", "RewardsCore", 9)


def main():
    threads_api = fetch_api_data()
    threads_db = load_db_data()

    print("=== GitHub API vs 数据库数据对比 ===")
    print()

    sourcery_api = []
    for t in threads_api:
        first_comment = t.get("comments", {}).get("nodes", [{}])[0] if t.get("comments") else {}
        author = first_comment.get("author", {}).get("login", "")
        if "sourcery" in author.lower():
            sourcery_api.append(t)

    sourcery_db = [t for t in threads_db if t.source == "Sourcery"]

    print(f"GitHub API Sourcery Thread 数: {len(sourcery_api)}")
    print(f"数据库 Sourcery Thread 数: {len(sourcery_db)}")
    print()

    print("GitHub API Sourcery Thread 状态:")
    for t in sourcery_api:
        path = t.get("path", "N/A")
        line = t.get("line", "None")
        is_resolved = t.get("isResolved", False)
        status = "✅ 已解决" if is_resolved else "⏳ 待处理"
        print(f"  {path}:{line} - {status}")

    print()

    print("数据库 Sourcery Thread 状态:")
    for t in sourcery_db:
        path = t.file_path or "N/A"
        line = t.line_number or "None"
        is_resolved = t.is_resolved
        local_status = t.local_status
        status = "✅ 已解决" if is_resolved else "⏳ 待处理"
        print(f"  {path}:{line} - {status} (local: {local_status})")

    print()

    print("=== 差异分析 ===")
    print()

    api_index = {}
    for t in sourcery_api:
        path = t.get("path", "")
        line = t.get("line")
        key = (path, line)
        api_index[key] = t

    db_index = {}
    for t in sourcery_db:
        path = t.file_path or ""
        line = t.line_number
        if line == 0:
            line = None
        key = (path, line)
        db_index[key] = t

    print("状态不一致的 Thread:")
    for key, api_t in api_index.items():
        if key in db_index:
            db_t = db_index[key]
            api_resolved = api_t.get("isResolved", False)
            db_resolved = db_t.is_resolved
            if api_resolved != db_resolved:
                print(f"  {key[0]}:{key[1]} - API: {api_resolved}, DB: {db_resolved}")

    print()

    print("API 有但数据库没有的 Thread:")
    for key in api_index:
        if key not in db_index:
            print(f"  {key[0]}:{key[1]}")

    print()

    print("数据库有但 API 没有的 Thread:")
    for key in db_index:
        if key not in api_index:
            print(f"  {key[0]}:{key[1]}")

    print()

    api_pending = sum(1 for t in sourcery_api if not t.get("isResolved"))
    db_pending = sum(1 for t in sourcery_db if not t.is_resolved)

    print(f"GitHub API 待处理 Sourcery Thread: {api_pending}")
    print(f"数据库待处理 Sourcery Thread: {db_pending}")


if __name__ == "__main__":
    main()
