---
task_id: <唯一ID>
created_at: <时间戳>
type: dev | test | docs
dev_retry_count: 0
max_retries: 3
status: pending | in_progress | completed | blocked
---

### 任务描述

<具体任务内容>

### 上下文信息

- 相关文件：<文件列表>
- 历史规则：<从 Memory MCP 检索的内容>

### 重试记录

| 轮次 | 时间 | 结果 | 备注 |
|------|------|------|------|
| 1 | <时间> | 失败 | <失败原因> |

### 状态

- [ ] 待执行
- [ ] 执行中
- [ ] 已完成
- [ ] 已阻塞
