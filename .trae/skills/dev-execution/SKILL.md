---
name: dev-execution
description: 开发执行详细流程。dev-agent 执行代码修改时调用。
---

# 开发执行详细流程

## 工作流程

### 1. 修改代码

修改业务代码（`src/` 等非测试目录）。

### 2. 局部验证（< 30秒）

```bash
ruff check .
ruff format --check .
mypy src/ --strict
pytest tests/<相关单文件>.py -v
```

### 3. 验证失败处理

- 调用【阅读】工具查看前一次终端完整日志
- 修复并重试（最大重试次数：3）

### 4. 触发阻断

若第 3 次重试仍失败，停止操作：

1. 生成 `blocked_reason.md`
2. 记录 3 种尝试过的修复方案
3. 附上完整 Traceback
4. 挂起等待 Master Agent 调度

## 输出格式（强制）

```
---
task_id: <任务ID>
status: success | blocked
---

### 变更摘要

- `<文件路径>`: <变更核心逻辑说明>

### 验证结果

- [ ] `ruff check` 通过
- [ ] `ruff format --check` 通过
- [ ] `mypy` 通过
- [ ] 局部单元测试通过

### 移交说明 (Handoff to test-agent)

- **验证入口**: `python main.py --task <具体命令>`
- **受影响模块**: `<具体文件或类名>`
- **需重点验证**: <如：代理切换时的 Session 保持>
```

## Memory MCP 知识库交互

1. **动手编码前 (`search_nodes`)**：检索目标文件或核心函数的 Entity，读取过去的 observations，确认是否有特殊的业务约束（如并发锁机制、特定的 API 字段转换规则）。
2. **禁止写入 Memory MCP**：如果发现需要记录的重要信息，返回给 Master Agent 处理。

## GitHub MCP 调用策略（条件触发）

仅在以下场景**必须**调用 GitHub MCP，其余时间优先依赖本地上下文：

1. **关联任务**：当用户指令包含 "Issue #..." 或 "PR #..." 时，使用 `get_issue` / `get_pull_request` 获取详细背景。
2. **未知报错**：当本地修复陷入僵局，无法理解报错原因时，使用 `search_issues` 搜索社区或历史解决方案。
3. **涉及第三方库升级时**：**建议**先使用 `search_code` 确认该库在项目中的其他引用位置，防止破坏性变更。

## 信息获取协议

为了防止幻觉和重复造轮子：

1. **收到报错修复任务时**：如果未提供完整 Log，**禁止**直接开始修改代码。**必须**先要求用户提供 Log，或尝试 `search_issues` 搜索类似错误。
2. **涉及第三方库升级时**：**建议**先使用 `search_code` 确认该库在项目中的其他引用位置，防止破坏性变更。
