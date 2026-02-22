---
name: master-execution
description: Master Agent 执行详细流程。任务路由、PR 管理、Git 操作。
---

# Master Agent 执行详细流程

## Git 规范

**目标**：保持历史整洁，避免碎片化 commit 导致其他分支变基困难。

### 提交策略

| 场景 | 操作 |
|------|------|
| 全新改动 | `git commit -m "message"` |
| 对上次 commit 的修正/补充 | `git commit --amend` |

### amend 用法

```bash
# 修正内容 + 修改信息
git commit --amend -m "新信息"

# 修正内容，保持原信息
git commit --amend --no-edit
```

### 时序

1. 任务完成 → commit
2. 发现需要修正 → amend（未 push 时）
3. 确认无误 → push

## 子 Agent 调用

| Agent | 场景 | 说明 |
|-------|------|------|
| `dev-agent` | 代码修改 | 业务代码编写与局部验证 |
| `test-agent` | 测试验收 | 全量测试与 E2E 验收 |
| `docs-agent` | 文档更新 | README/CHANGELOG 同步 |

**注意**：Master Agent 没有 Playwright MCP，所有 E2E 测试必须交给 test-agent。

## Skills 调用

| Skill | 时机 | 说明 |
|-------|------|------|
| `mcp-acceptance` | 代码修改完成后 | 执行 7 阶段验收 |
| `pr-review` | PR 创建后 | 处理 AI 审查，通知人工合并 |
| `fetch-reviews` | `pr-review` 内部调用 | 获取 Sourcery/Copilot/Qodo 评论 |

**注意**：
- `fetch-reviews` 由 `pr-review` 内部调用，无需单独调用
- 项目要求合并前解决所有对话，Copilot/Qodo 评论无法标记解决，因此 **合并需人工确认**

## 任务路由流程

```
用户请求 → 规划任务
    │
    ├─ 代码修改 → dev-agent
    │
    ├─ 测试验收 → test-agent
    │
    └─ 文档更新 → docs-agent
```

## 合并限制

项目要求合并前必须解决所有对话：

- **Sourcery**：自动检测 `✅ Addressed`
- **Copilot/Qodo**：无法通过 API 标记解决，需人工在 GitHub 网页点击"Resolve conversation"

**结论**：Agent 无法自主合并 PR，需人工确认。
