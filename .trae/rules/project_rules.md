# RewardsCore 项目规则

## 身份判定

- **如果没有被明确指定身份** → 你是 Trae 内置的 solo coder（Master Agent）
- **如果被明确指定身份** → 按照你的身份阅读对应提示词

## 路由表

| 身份 | 配置文件 |
|------|---------|
| solo coder (Master) | `.trae/prompts/master.md` |
| dev-agent | `.trae/agents/dev-agent.md`（UI 配置） |
| test-agent | `.trae/agents/test-agent.md`（UI 配置） |
| docs-agent | `.trae/agents/docs-agent.md`（UI 配置） |

## 公共规则

### Git 规范

- 遵循 Conventional Commits
- **必须使用中文**描述

### 测试规范

- 改动前后必须运行自动化测试
- 测试失败时自排查闭环

### AI 审查处理

- **必须修复**：`bug_risk`, `Bug`, `security` 标签
- **自主决断**：`suggestion`, `performance` 标签

---

**Skills**：`mcp-acceptance`, `pr-review`, `fetch-reviews`
