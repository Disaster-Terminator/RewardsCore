# RewardsCore-Diagnosis 项目规则

## 1. MCP 工具优先

验收时使用 Playwright/GitHub MCP 直接验证，拒绝仅依赖日志推断。

* **Playwright MCP**：阶段 4-5 无头验收
* **GitHub MCP**：阶段 6-7 PR 管理（合并需人工确认）
* **Memory MCP**：跨会话知识持久化

## 2. 测试驱动

改动前后必须运行自动化测试，失败时自排查闭环（查阅日志、诊断报告），仅在修复无效时向开发者求助。

## 3. 验收流程

调用 `mcp-acceptance` Skill 执行 7 阶段验收：

```text
阶段 1-3: CI 自动化（静态检查 → 单元测试 → 集成测试）
阶段 4-5: MCP 无头验收（Dev无头 → User无头）
阶段 6-7: PR 管理（创建PR → 等待审查 → 合并确认）
```

## 4. 阻塞点

* 阶段 5 后：等待"本地审查通过"
* 阶段 6 后：等待"在线审查通过"
* 合并 PR：需人工确认

## 5. AI 审查处理

* **必须修复**：`bug_risk`, `Bug`, `security` 标签
* **自主决断**：`suggestion`, `performance` 标签
* **无法修复**：向开发者求助

## 6. Git 自主权限

### 可自主执行

* `git add`, `git commit`, `git push`
* `git pull --rebase`
* `git checkout -b`, `git branch -d`（本地分支）
* `git commit --amend`（仅未 push 时）

### 需人工确认

* `git commit --amend`（已 push）
* `git rebase`（已 push）
* `git push --force`
* `merge PR`
* 删除远程分支

---
**参考文档**：`docs/reference/MCP_WORKFLOW.md`, `docs/reference/BRANCH_GUIDE.md`
