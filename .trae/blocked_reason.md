---
task_id: <任务ID>
agent: <Agent 名称>
created_at: <时间戳>
reason_type: missing_context | logic_unimplementable | mcp_failure | retry_exhausted
---

### 阻塞原因

<描述为什么无法继续执行>

### 原因类型说明

| 类型 | 含义 | 恢复策略 |
|------|------|----------|
| `missing_context` | 缺少 DOM 结构等上下文 | Master 调用 test-agent 嗅探，携新数据重试 |
| `logic_unimplementable` | 核心逻辑无法实现 | 停止流转，交出控制权给人类 |
| `mcp_failure` | MCP 调用连续失败 | Master 检查 MCP 配置，人工干预 |
| `retry_exhausted` | 重试次数耗尽（熔断触发） | 人工审查后决定是否继续 |

### 需要的信息

- [ ] DOM 结构：<URL 或选择器>
- [ ] 日志：<需要的日志类型>
- [ ] 其他：<具体描述>

### 已尝试的方案

1. <方案 1>
2. <方案 2>
3. <方案 3>

### Traceback（最后 10 行）

```
<错误堆栈，最多 10 行>
```
