---
task_id: mcp-acceptance-20260223
created_at: 2026-02-23T00:00:00Z
type: test
dev_retry_count: 0
max_retries: 3
status: in_progress
---

### 任务描述

执行 MCP 驱动的 7 阶段验收流程，完整测试多智能体框架。

### 验收阶段

**阶段 1-3: CI 自动化**
- [ ] 阶段 1：静态检查 (`ruff check . && ruff format --check .`)
- [ ] 阶段 2：单元测试 (`pytest tests/unit/ -m "not real" -v`)
- [ ] 阶段 3：集成测试 (`pytest tests/integration/ -v`)

**阶段 4-5: MCP 无头验收**
- [ ] 阶段 4：Dev 无头验证 (`rscore --dev --headless` 或降级到 `python main.py --dev --headless`)
- [ ] 阶段 5：User 无头验证 (`rscore --user --headless` 或降级到 `python main.py --user --headless`)

### 上下文信息

- 项目：RewardsCore-Diagnosis
- 测试框架：pytest
- 静态检查：ruff
- 无头验收：Playwright MCP
- 环境配置：environment.yml / pyproject.toml

### 降级执行策略

如果 `rscore` 命令失败，必须降级到 `python main.py` 执行，禁止跳过。

### 状态

- [x] 待执行
- [x] 执行中
- [ ] 已完成
- [ ] 已阻塞
