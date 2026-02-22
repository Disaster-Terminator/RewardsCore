---
name: fetch-reviews
description: 获取所有审查机器人评论。Qodo 使用 WebFetch，Sourcery/Copilot 使用 GitHub MCP。
---

# 获取审查意见

## 触发条件

- PR 创建后需要查看审查意见
- 需要检查审查状态

## 仓库信息

| 属性 | 值 |
|------|-----|
| owner | `Disaster-Terminator` |
| repo | `RewardsCore` |

## 获取策略

### Sourcery 和 Copilot

使用 GitHub MCP：
```
get_pull_request_comments(owner, repo, pull_number)
get_pull_request_reviews(owner, repo, pull_number)
```

### Qodo

**必须使用 WebFetch**（GitHub MCP 会截断数据）：

```
WebFetch(url="https://api.github.com/repos/{owner}/{repo}/pulls/{number}/comments")
```

过滤条件：`user.login == "qodo-code-review[bot]"`

## 解析策略

### Sourcery

1. 过滤 `user.login == "sourcery-ai[bot]"`
2. 提取 `<details><summary>Prompt for AI Agents</summary>` 中的 `~~~markdown` 块
3. 解析 Individual Comments 部分

### Copilot

1. 过滤 `user.login == "copilot-pull-request-reviewer[bot]"`
2. 直接读取 body（纯 Markdown）

### Qodo

1. 过滤 `user.login == "qodo-code-review[bot]"`
2. 解析 `body` 中的 HTML：
   - 提取 `<details><summary><strong>Agent Prompt</strong></summary>` 中的内容
   - 提取 `Fix Focus Areas` 列表
3. 问题类型：
   - 🐞 Bug：必须修复
   - 📘 Rule violation：必须修复
   - ⛨ Security：必须修复
   - 🏯 Reliability：必须修复

## 输出格式

### 审查意见汇总

| 来源 | 类型 | 问题 | 文件 | 状态 |
|------|------|------|------|------|
| Sourcery | bug_risk | ... | ... | 待修复 |
| Copilot | suggestion | ... | ... | 自主决断 |
| Qodo | Bug | ... | ... | 待修复 |
