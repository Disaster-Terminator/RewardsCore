# Checklist

## 数据模型 (`src/review/models.py`)

- [ ] `ReviewThreadState` 模型存在
- [ ] `id` 字段定义为 Thread ID（GraphQL Node ID）
- [ ] `is_resolved` 字段表示 GitHub 上的解决状态
- [ ] `local_status` 字段表示本地处理状态（pending/resolved/ignored）
- [ ] `primary_comment_body` 字段存储第一条评论内容
- [ ] `comment_url` 字段存储评论 URL
- [ ] `source` 字段存储评论来源
- [ ] `file_path` 和 `line_number` 字段存储位置信息
- [ ] `resolution_type` 字段存储解决依据类型

## Qodo 解析器 (`src/review/parsers.py`)

- [ ] 正则表达式使用行首锚点 `^`
- [ ] 匹配 `☑` (U+2611) 符号
- [ ] 匹配 `✅ Addressed` 短语（必须跟 Addressed）
- [ ] 兼容 Markdown 列表符号 (`-` 或 `*`)
- [ ] 忽略大小写
- [ ] `is_auto_resolved` 方法正确实现
- [ ] `detect_source` 方法正确识别 Sourcery/Qodo/Copilot

## GraphQL 客户端 (`src/review/graphql_client.py`)

- [ ] `fetch_pr_threads` 返回 Thread ID（而非 Comment ID）
- [ ] `fetch_pr_threads` 返回 `isResolved` 字段
- [ ] `fetch_pr_threads` 返回 `path` 和 `line` 字段
- [ ] `resolve_thread` mutation 正确实现
- [ ] `reply_to_thread` mutation 正确实现
- [ ] 错误处理和日志记录完善

## 状态管理器 (`src/review/comment_manager.py`)

- [ ] TinyDB 初始化正确
- [ ] `save_threads` 方法实现 upsert 逻辑
- [ ] 远端状态同步：`isResolved=true` 时强制更新 `local_status` 为 `resolved`
- [ ] 远端状态同步：`resolution_type` 标记为 `manual_on_github`
- [ ] `mark_resolved_locally` 方法正确更新状态
- [ ] `get_pending_threads` 方法正确过滤
- [ ] FileLock 确保并发安全

## 整合器 (`src/review/resolver.py`)

- [ ] `resolve_thread` 方法遵循 "API First, DB Second" 原则
- [ ] 先调用 GitHub API，成功后再更新本地 DB
- [ ] API 失败时不更新本地状态
- [ ] 回复功能集成到解决流程中

## CLI 入口 (`tools/manage_reviews.py`)

- [ ] `resolve` 子命令正确实现
- [ ] `fetch` 子命令正确实现
- [ ] `list` 子命令正确实现
- [ ] JSON 输出格式正确

## Skill 文档更新

- [ ] `resolve-review-comment` skill 调用 Python CLI
- [ ] `fetch-reviews` skill 使用新的 GraphQL 查询
- [ ] 旧的 Playwright 逻辑标记为 DEPRECATED

## 测试覆盖

- [ ] Thread ID 获取测试通过
- [ ] 解决评论 API 调用测试通过
- [ ] Qodo 解析边界情况测试通过（包括 Markdown 列表格式）
- [ ] API 失败时数据一致性测试通过
- [ ] 远端状态同步测试通过（isResolved=true 覆盖本地 pending）
