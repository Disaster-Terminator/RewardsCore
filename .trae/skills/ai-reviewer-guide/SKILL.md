---
name: ai-reviewer-guide
description: AI审查工具参考指南。提供Sourcery/Copilot/Qodo的评论类型、解决状态检测、交互命令等详细信息。
---

# AI 审查工具参考指南

## Sourcery

### 评论结构

```
reviews.body 结构：
├── 总览意见（Overall Comments）- 无解决状态
│   └── "In MSRewardsApp.__init__ the diagnosis_reporter..."
└── <details><summary>Prompt for AI Agents</summary>
    └── ## Individual Comments
        ├── ### Comment 1
        │   ├── <location> `file.py:42` </location>
        │   └── <issue_to_address>问题描述</issue_to_address>
        └── ### Comment 2
            └── ...
```

### 类型判断

| 标签 | 含义 | 处理方式 |
|------|------|----------|
| `bug_risk` | 潜在 Bug | 必须修复 |
| `security` | 安全问题 | 必须修复 |
| `suggestion` | 代码建议 | 自主决断 |
| `performance` | 性能建议 | 自主决断 |

### 解决状态检测

- **已解决**：body 含 `✅ Addressed in {commit}`
- **数据源**：`get_pull_request_comments` 返回的行级评论

### 交互命令

| 命令 | 用途 |
|------|------|
| `@sourcery-ai review` | 触发新审查 |
| `@sourcery-ai resolve` | 解决所有评论 |
| `@sourcery-ai dismiss` | 关闭所有审查 |

---

## Qodo

### 评论类型

| 类型 | 内容 | 发送方式 | API返回 |
|------|------|----------|---------|
| **Code Review by Qodo** | 问题列表（Bug/Rule violation等） | review comment | ❌ 截断 |
| **PR Reviewer Guide 🔍** | 审查指南（工作量、安全、重点区域） | issue comment | ❌ 无 |

### 特征标记

| 标记 | 类型 | 处理方式 |
|------|------|----------|
| 🐞 Bug | Bug | 必须修复 |
| 📘 Rule violation | 规则违反 | 必须修复 |
| ⛨ Security | 安全问题 | 必须修复 |
| ⚯ Reliability | 可靠性问题 | 必须修复 |
| Correctness | 正确性问题 | 自主决断 |

### 解决状态检测

**Code Review by Qodo**：
- **已解决**：评论行开头有 `☑ ☑ ☑ ☑`（注意有空格）
- **重要**：`✓` 符号是类型前缀，不是已解决标志！

**PR Reviewer Guide 🔍**：
- 完成状态：**待测试确认**
- 当前处理方式：直接报告给用户，不判断解决状态

### 交互命令

| 命令 | 用途 |
|------|------|
| `/review` | PR 审查 |
| `/describe` | 生成 PR 描述 |
| `/improve` | 代码建议 |
| `/checks ci_job` | CI 反馈 |

---

## Copilot

### 类型判断

| 类型 | 处理方式 |
|------|----------|
| 代码建议块（```suggestion） | 自主决断 |
| 安全警告 | 必须修复 |

### 解决状态检测

- 无自动解决状态
- 需人工在 GitHub 网页标记解决

### 交互命令

- 无命令交互，自动审查

---

## 处理建议汇总

| 评论类型 | Agent 行为 |
|----------|------------|
| `bug_risk`, `Bug`, `Security`, `Rule violation`, `Reliability` | 报告给用户，等待修复指令 |
| `suggestion`, `performance`, `Correctness` | 报告给用户，自主决断是否采纳 |
| PR Reviewer Guide | 直接报告给用户 |

## 合并提醒

- **Agent 不自动合并 PR**，需通知用户确认
- Sourcery 可用 `@sourcery-ai resolve` 批量解决
- Copilot/Qodo 需人工处理
