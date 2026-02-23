---
name: fetch-reviews
description: 获取PR的AI审查评论。解析Sourcery/Copilot/Qodo评论并汇总未解决问题。
---

# AI 审查获取流程

## 触发条件

- 用户请求获取审查评论
- 用户请求查看PR状态

## 获取流程

### 步骤 1：GitHub MCP 获取评论

```
get_pull_request_reviews(owner, repo, pull_number)
get_pull_request_comments(owner, repo, pull_number)
get_pull_request_status(owner, repo, pull_number)
```

**Sourcery 数据提取**：

- 从 `reviews.body` 提取 "Prompt for AI Agents" 中的问题列表
- 从 `comments.body` 提取解决状态（`✅ Addressed`）

**注意**：GitHub API 对 Qodo 评论会截断。

### 步骤 2：Playwright MCP 获取 Qodo 完整评论

**必须使用 Playwright**，因为 GitHub API 会截断 Qodo 评论。

```javascript
// 1. 无头模式导航
playwright_navigate(url="https://github.com/{owner}/{repo}/pull/{number}", headless=true)

// 2. 提取 Qodo 评论
playwright_evaluate(script=`
(function() {
  let results = [];
  let comments = document.querySelectorAll('.markdown-body');
  comments.forEach(c => {
    let text = c.innerText;
    if (text.includes('PR Reviewer Guide') || 
        text.includes('Code Review by Qodo') ||
        text.includes('Rule violation')) {
      results.push(text);
    }
  });
  return results.join('\\n---\\n');
})()
`)

// 3. 关闭浏览器
playwright_close()
```

### 步骤 3：解析评论类型

详见 `ai-reviewer-guide` skill。

**快速参考**：

| 来源 | 已解决标志 |
|------|-----------|
| Sourcery | `✅ Addressed in {commit}` |
| Qodo (Code Review) | `☑ ☑ ☑ ☑` |
| Qodo (PR Reviewer Guide) | **待测试确认** |
| Copilot | 无 |

---

## 输出格式

```markdown
## AI 审查评论摘要

### 审查指南（Qodo PR Reviewer Guide）

| 项目 | 内容 |
|------|------|
| 审查工作量 | X/5 |
| 测试覆盖 | ✅/❌ |
| 安全问题 | 有/无 |
| 关注重点 | ... |

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

---

## 处理建议

| 评论类型 | Agent 行为 |
|----------|------------|
| `bug_risk`, `Bug`, `Security`, `Rule violation`, `Reliability` | 报告给用户，等待修复指令 |
| `suggestion`, `performance`, `Correctness` | 报告给用户，自主决断是否采纳 |
| PR Reviewer Guide | 直接报告给用户 |

## 合并提醒

- **Agent 不自动合并 PR**，需通知用户确认
- 详细命令参考见 `ai-reviewer-guide` skill
