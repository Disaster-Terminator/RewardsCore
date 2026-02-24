# PR 在线机器人评论审查规律汇总

> 最后更新: 2026-02-24

本文档汇总了 PR 审查评论处理系统的所有核心规律，作为日常工作的快速参考。

---

## 一、核心概念

### 1.1 操作对象 vs 参考对象

| 类型 | 模型 | 用途 | 操作 |
|------|------|------|------|
| **Thread** | `ReviewThreadState` | 主要操作对象 | 可解决、可回复 |
| **Overview** | `ReviewOverview` | 只读参考 | 仅确认已阅读 |
| **IssueCommentOverview** | `IssueCommentOverview` | 只读参考 | 仅阅读，不可操作 |

**核心原则**：Agent 主要操作 Thread 数据。Overview 用于了解 PR 整体评价和高层建议。

---

## 二、三种 AI 审查工具对比

### 2.1 工具标识

| 工具 | GitHub 用户名 | 评论来源 | 说明 |
|------|--------------|----------|------|
| **Sourcery** | `sourcery-ai bot` | Review Thread | 代码审查 |
| **Qodo** | `qodo-code-review bot` | Review Thread | Code Review（当前使用） |
| **Copilot** | `Copilot AI` | Review Thread | 代码审查 |

### 2.2 特征对比

| 特性 | Sourcery | Qodo | Copilot |
|------|----------|------|---------|
| **结构化摘要** | `Prompt for AI Agents` | `Code Review` | 无 |
| **动态解决状态** | ✅ 自动更新 | ❌ 无 | ❌ 无 |
| **行级评论解决** | `@sourcery-ai resolve` 或 API | **必须用 API** | GitHub API |
| **重审机制** | 全新完整审查 | 更新 Code Review | 无 |
| **斜杠命令** | `@sourcery-ai review` | `/agentic_review` | 无 |

### 2.3 关键区分：代码变化摘要 vs 改进意见

**代码变化摘要（非改进意见，不需要处理）**：

| 来源 | 标题 | 存储位置 |
|------|------|----------|
| Sourcery | "Reviewer's Guide" | Review body |

**改进意见摘要（需要处理）**：

| 来源 | 标题 | 存储位置 |
|------|------|----------|
| Sourcery | "Prompt for AI Agents" | Review body |
| Qodo | 逐行评论（Review Thread） | Review Thread |

---

## 三、问题分类规则

### 3.1 必须修复（红色）

以下问题类型必须修复，Agent 应报告用户等待修复指令：

| 来源 | 问题类型 | 颜色 |
|------|----------|------|
| Qodo | Bug | 🔴 |
| Qodo | Security | 🔴 |
| Qodo | Rule violation | 🔴 |
| Qodo | Reliability | 🔴 |
| Sourcery | bug_risk | 🔴 |
| Sourcery | security | 🔴 |
| Copilot | 安全警告 | 🔴 |

### 3.2 自主决断（黄色）

以下问题类型可由 Agent 自主决定是否采纳：

| 来源 | 问题类型 | 颜色 |
|------|----------|------|
| Qodo | Correctness | 🟡 |
| Sourcery | suggestion | 🟡 |
| Sourcery | performance | 🟡 |
| Copilot | suggestion 代码块 | 🟡 |

### 3.3 问题类型判断代码

```python
MUST_FIX_TYPES = {"Bug", "Security", "Rule violation", "Reliability", "bug_risk", "security"}

def is_must_fix(issue_type: str) -> bool:
    for type_name in MUST_FIX_TYPES:
        if type_name.lower() in issue_type.lower():
            return True
    return False
```

---

## 四、数据模型

### 4.1 ReviewThreadState（核心操作对象）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | Thread ID（用于解决操作） |
| `source` | string | 来源：Sourcery / Qodo / Copilot |
| `local_status` | string | 状态：pending / resolved / ignored |
| `is_resolved` | boolean | GitHub 上的解决状态（只读） |
| `file_path` | string | 文件路径 |
| `line_number` | int \| None | 行号，None 表示文件级评论 |
| `primary_comment_body` | string | 评论内容 |
| `enriched_context` | EnrichedContext | 结构化元数据（可选） |

### 4.2 EnrichedContext

| 字段 | 类型 | 说明 |
|------|------|------|
| `issue_type` | string | 问题类型（Bug / Security / suggestion 等） |
| `issue_to_address` | string | 问题描述（来自 Sourcery Prompt） |
| `code_context` | string | 代码上下文（来自 Sourcery Prompt） |

---

## 五、CLI 命令

### 5.1 获取评论

```bash
python tools/manage_reviews.py fetch --owner {owner} --repo {repo} --pr {pr_number}
```

### 5.2 列出评论

```bash
# 表格格式（默认）
python tools/manage_reviews.py list --status pending

# JSON 格式
python tools/manage_reviews.py list --status pending --format json

# 按来源过滤
python tools/manage_reviews.py list --source Qodo
```

### 5.3 解决评论

```bash
python tools/manage_reviews.py resolve --thread-id {thread_id} --type {resolution_type} [--reply "{reply_content}"]
```

### 5.4 确认总览意见

```bash
# 确认所有总览意见
python tools/manage_reviews.py acknowledge --all

# 确认单个总览意见
python tools/manage_reviews.py acknowledge --id {overview_id}
```

---

## 六、解决规则

### 6.1 解决类型

| 类型 | 含义 | 需要回复 |
|------|------|----------|
| `code_fixed` | 代码已修复 | 否 |
| `adopted` | 已采纳建议 | 否 |
| `rejected` | 拒绝建议 | **是** |
| `false_positive` | 误报 | **是** |
| `outdated` | 已过时 | 否 |

### 6.2 回复说明规则

| 情况 | 是否回复 | 回复内容 |
|------|----------|----------|
| 代码已修复 | 否 | - |
| 已采纳建议 | 否 | - |
| 拒绝建议 | 是 | 说明拒绝原因 |
| 误报 | 是 | 说明为何是误报 |
| 过时 | 否 | - |

### 6.3 Sourcery 动态解决状态

**重要规律**：Sourcery 会根据新推送的 commit 自动检测并更新评论状态：

- 当代码修改解决了某个评论时，Sourcery 会自动标记为 `✅ Addressed in {commit_hash}`
- 这意味着待处理评论数量会随 commit 动态变化
- **获取评论前应确保数据是最新的（重新 fetch）**

---

## 七、Qodo 特殊规则

### 7.1 Code Review

- **触发方式**：`/agentic_review` 斜杠命令（PR 创建时自动执行）
- **产物**：逐行评论（Review Thread）
- **更新方式**：再次执行 `/agentic_review` 更新
  - 在原 Issue Comment 添加更新说明：`Persistent review updated to latest commit <hash>`
  - 新增逐行评论（Review Thread）

### 7.2 逐行评论处理规则

> 项目设定 `inline_comments_severity_threshold: 1`，**所有等级的意见都会成为逐行评论**。

| 等级 | 名称 | 说明 |
|------|------|------|
| 1 | Informational | 信息提示/代码风格微调 |
| 2 | Remediation Recommended | 建议修复，如潜在逻辑隐患 |
| 3 | Action Required | 必须采取行动，如安全漏洞、严重 Bug |

**处理规则**：

- 所有逐行评论都必须得到解决
- 无论是否接受，都必须调用 CLI 工具来处理

### 7.3 状态标记

- **已解决**：`☑`（一个勾）在评论行开头
- **注意**：`✓` 符号是类型前缀（如 `✓ Correctness`），不是已解决标志！

### 7.4 无法通过 @ 解决

- Qodo 行级评论**无法通过 @ 解决**
- 必须调用 GitHub API

---

## 八、降级策略

如果 CLI 工具失败，参考 `docs/reference/archive/v1-ai-reviewer-guide.md` 使用 Playwright 手动获取评论。

---

## 九、严禁事项

| 禁止行为 | 原因 |
|----------|------|
| 一次性解决所有评论 | 每个评论必须单独处理 |
| 无依据标记解决 | 必须先确认问题已解决或有合理理由 |
| 批量操作 | 必须逐个评论处理 |
| 跳过说明评论 | rejected/false_positive 必须回复说明原因 |
| 忽略必须修复项 | Bug/Security 类型必须报告用户 |
| 跳过总览意见确认 | 总览意见应确认已阅读 |
| 自动合并 PR | 需通知用户确认 |

---

## 十、工作流示例

```
1. 获取评论状态
   python tools/manage_reviews.py list --status pending --format json

2. 分类处理
   - 遍历 threads，检查 enriched_context.issue_type
   - 必须修复项（Bug/Security）→ 停止，报告用户
   - 自主决断项（suggestion）→ Agent 决定是否采纳

3. 解决已修复项
   python tools/manage_reviews.py resolve --thread-id ID --type code_fixed

4. 拒绝不采纳项
   python tools/manage_reviews.py resolve --thread-id ID --type rejected --reply "原因"

5. 确认总览意见
   python tools/manage_reviews.py acknowledge --all
```

---

## 相关文档

- [fetch-reviews Skill](../../.trae/skills/fetch-reviews/SKILL.md)
- [resolve-review-comment Skill](../../.trae/skills/resolve-review-comment/SKILL.md)
- [评论处理系统说明](评论处理系统说明.md)
- [审查评论处理工作流指南](审查评论处理工作流指南.md)
- [v1 AI 审查工具参考指南（归档）](archive/v1-ai-reviewer-guide.md)
