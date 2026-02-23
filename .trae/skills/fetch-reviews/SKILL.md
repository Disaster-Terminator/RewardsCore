---
name: fetch-reviews
description: 获取PR的AI审查评论。分析Sourcery/Copilot/Qodo评论类型并报告给用户。
---

# AI 审查获取流程

## 触发条件

- 用户创建 PR 后
- 用户请求获取审查评论

## 获取流程（强制）

### 步骤 1：GitHub MCP 获取 Sourcery/Copilot 评论

```
get_pull_request_comments(owner, repo, pull_number)
get_pull_request_reviews(owner, repo, pull_number)
get_pull_request_status(owner, repo, pull_number)
```

**注意**：GitHub API 返回的 Qodo 评论会被截断，**必须**使用 Playwright MCP 获取完整内容。

### 步骤 2：Playwright MCP 获取 Qodo 完整评论（强制）

**Qodo 评论必须通过 Playwright MCP 获取**，因为 GitHub API 会截断长评论。

```javascript
// 1. 导航到 PR 页面
playwright_navigate(url="https://github.com/{owner}/{repo}/pull/{number}")

// 2. 提取 Qodo 评论
playwright_evaluate(script=`
(function() {
  let comments = document.querySelectorAll('.markdown-body');
  let qodoComments = [];
  comments.forEach(c => {
    let text = c.innerText;
    if (text.includes('Rule violation') || text.includes('Bug') || text.includes('Reliability') || text.includes('Code Review by Qodo')) {
      qodoComments.push(text);
    }
  });
  return qodoComments.join('\\n---\\n');
})()
`)

// 3. 关闭浏览器
playwright_close()
```

### 步骤 3：汇总所有评论

将 GitHub MCP 和 Playwright MCP 获取的评论合并，按类型分类输出。

---

## 评论类型判断逻辑

### Sourcery 评论

**特征**：评论 body 含 `**issue (bug_risk):**` 或 `**issue (security):**`

| 标签 | 含义 | 处理方式 |
|------|------|----------|
| `bug_risk` | 潜在 Bug | 必须修复 |
| `security` | 安全问题 | 必须修复 |
| `suggestion` | 代码建议 | 自主决断 |
| `performance` | 性能建议 | 自主决断 |

**解决状态**：检查 body 是否含 `✅ Addressed`

#### Sourcery 交互命令

通过在 PR 评论中提及 `@sourcery-ai` 触发：

| 命令 | 用途 | 说明 |
|------|------|------|
| `@sourcery-ai review` | 触发新审查 | 推送新 commit 后重新审查 |
| `@sourcery-ai resolve` | 解决所有评论 | 已处理所有评论后清理 |
| `@sourcery-ai dismiss` | 关闭所有审查 | 重新开始时使用 |
| `@sourcery-ai title` | 生成 PR 标题 | 自动生成标题 |
| `@sourcery-ai summary` | 生成 PR 摘要 | 自动生成摘要 |
| `@sourcery-ai guide` | 生成审查指南 | 生成 Reviewer's Guide |
| `@sourcery-ai issue` | 创建 Issue | 从评论创建 Issue |

### Copilot 评论

**特征**：评论含 ````suggestion` 代码建议块

| 类型 | 处理方式 |
|------|----------|
| 代码建议块 | 自主决断 |
| 安全警告 | 必须修复 |

**注意**：Copilot 评论无法通过 API 标记解决，需人工处理。

### Qodo 评论

**特征**：评论含以下标记

| 标记 | 类型 | 处理方式 |
|------|------|----------|
| 🐞 Bug | Bug | 必须修复 |
| 📘 Rule violation | 规则违反 | 必须修复 |
| ⛨ Security | 安全问题 | 必须修复 |
| ⚯ Reliability | 可靠性问题 | 必须修复 |
| Correctness | 正确性问题 | 自主决断 |

**重要**：`✓` 符号是类型前缀，**不是**已解决标志！

**已解决状态**：

- `☑ ☑ ☑ ☑` 符号表示已解决（注意有空格分隔）
- 标题被 `<s>` 标签划掉表示已解决

**判断逻辑**：

```
已解决 = 评论行开头有 "☑ ☑ ☑ ☑"
未解决 = 评论行没有 "☑ ☑ ☑ ☑"
```

#### Qodo 交互命令

通过在 PR 评论中使用斜杠命令触发：

| 命令 | 用途 | 说明 |
|------|------|------|
| `/review` | PR 审查 | 可调节的反馈，包括问题、安全、审查工作量等 |
| `/describe` | 生成 PR 描述 | 自动生成标题、类型、摘要、代码演示和标签 |
| `/improve` | 代码建议 | 改进 PR 的代码建议 |
| `/checks ci_job` | CI 反馈 | 分析失败的 CI 任务 |
| `/ask ...` | 问答 | 回答关于 PR 或特定代码行的问题 |
| `/analyze` | 分析 | 识别变更的代码组件，交互式生成测试、文档、建议 |
| `/test` | 生成测试 | 为选定组件自动生成单元测试 |
| `/implement` | 实现 | 从审查建议生成实现代码 |

---

## 输出格式

### 评论摘要

```markdown
## AI 审查评论摘要

### 必须修复

| 来源 | 类型 | 文件 | 行号 | 描述 |
|------|------|------|------|------|
| Sourcery | bug_risk | xxx.py | 42 | ... |
| Qodo | Security | yyy.py | 15 | ... |

### 建议性评论

| 来源 | 类型 | 文件 | 描述 |
|------|------|------|------|
| Sourcery | suggestion | xxx.py | ... |
| Copilot | suggestion | yyy.py | ... |

### 已解决

| 来源 | 文件 | 状态 |
|------|------|------|
| Sourcery | xxx.py | ✅ Addressed |
| Qodo | yyy.py | ☑☑☑☑ |
```

## 处理建议

| 评论类型 | Agent 行为 |
|----------|------------|
| `bug_risk`, `Bug`, `Security`, `Rule violation`, `Reliability` | 报告给用户，等待修复指令 |
| `suggestion`, `performance`, `Correctness` | 报告给用户，自主决断是否采纳 |

## 合并提醒

- Sourcery 评论可自动检测 `✅ Addressed`，也可用 `@sourcery-ai resolve` 批量解决
- Copilot/Qodo 评论需人工在 GitHub 网页标记解决
- **Agent 不自动合并 PR**，需通知用户确认

## 解决状态检测汇总

| 机器人 | 已解决标志 | 可否通过命令解决 |
|--------|-----------|------------------|
| Sourcery | `✅ Addressed in {commit}` | ✅ `@sourcery-ai resolve` |
| Copilot | 无 | ❌ 需人工处理 |
| Qodo | ☑☑☑☑ 或 `<s>` 标签 | ❌ 需人工处理 |

## 交互命令汇总

| 机器人 | 命令格式 | 常用命令 |
|--------|----------|----------|
| Sourcery | `@sourcery-ai <command>` | `review`, `resolve`, `dismiss` |
| Qodo | `/<command>` | `/review`, `/describe`, `/improve`, `/checks` |
| Copilot | 无命令交互 | 自动审查 |
