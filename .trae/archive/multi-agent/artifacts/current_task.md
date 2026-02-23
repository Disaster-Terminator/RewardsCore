---
task_id: mcp-acceptance-test
status: in_progress
created_at: 2026-02-23
---

# 验收任务

执行 MCP 驱动的 7 阶段验收流程，重点关注：

1. **rscore 入口点问题** - 验证 `src/cli.py` 修复是否生效
2. **二维错误诊断矩阵** - 验证降级策略是否正确执行
3. **MCP 使用时机** - 观察 Playwright MCP 的调用时机

## 执行范围

- 阶段 1-3: CI 自动化
- 阶段 4: Dev 无头验证
- 阶段 5: User 无头验证（如有会话文件）

## 验收标准

- rscore 成功运行，或降级到 python main.py 成功
- 二维错误诊断矩阵正确归因
