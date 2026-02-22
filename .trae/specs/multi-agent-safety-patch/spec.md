# 多智能体框架安全补丁 Spec

## Why

当前框架在工程化设计上已达到极高成熟度，但在面对 Microsoft Rewards 这类存在极强对抗性（反爬、A/B 测试）的业务流时，存在三个致命盲区：

1. **状态机死锁**：`[dev-agent] ↔ [test-agent]` 无限循环崩溃（Ping-Pong Effect）
2. **上下文爆炸**：媒介文件追加写入导致上下文窗口撑爆
3. **代码覆灭风险**：缺少回滚机制，dev-agent 可能改坏基建代码

## What Changes

### **BREAKING** 架构补丁

1. **熔断器机制**：在 `current_task.md` 中引入 `dev_retry_count` 字段，限制重试次数
2. **强制覆写策略**：媒介文件必须使用覆写模式，禁止追加
3. **微提交保护**：Master Agent 在路由前强制执行 `git stash` 或临时 commit

### 新增 Skill

- `master-recovery`：处理挂起任务的恢复流程

### 新增元数据字段

```yaml
---
task_id: req-001
dev_retry_count: 2
max_retries: 3
status: in_progress
---
```

## Impact

- 受影响的文件：
  - `.trae/rules/project_rules.md`（新增熔断器规则）
  - `.trae/current_task.md`（新增元数据字段）
  - `.trae/skills/test-execution/SKILL.md`（覆写策略 + 精简取证）
  - `.trae/skills/dev-execution/SKILL.md`（重试计数检查）
  - `.trae/skills/master-execution/SKILL.md`（微提交保护 + 恢复流程）
  - `.trae/skills/master-recovery/SKILL.md`（新增）
  - `.trae/agents/test-agent.md`（取证规范约束）

---

## ADDED Requirements

### Requirement: 熔断器机制（Circuit Breaker）

系统必须在任务路由层面实现熔断器，防止无限循环崩溃。

#### Scenario: 重试次数超限

- **WHEN** Master Agent 路由任务给 dev-agent
- **AND** `dev_retry_count` 已达到 `max_retries`（默认 3）
- **THEN** 禁止流转给 dev-agent
- **AND** 必须触发挂起并通知人类开发者

#### Scenario: 重试计数递增

- **WHEN** test-agent 报告测试失败
- **AND** Master Agent 准备路由回 dev-agent
- **THEN** 必须先递增 `dev_retry_count`
- **AND** 检查是否达到上限

### Requirement: 媒介文件覆写策略

系统必须强制媒介文件使用覆写模式，防止上下文爆炸。

#### Scenario: 测试报告覆写

- **WHEN** test-agent 写入 `test_report.md`
- **THEN** 必须使用完全覆写（Overwrite）模式
- **AND** 禁止追加写入（Append）

#### Scenario: 阻塞原因覆写

- **WHEN** 任意 Agent 写入 `blocked_reason.md`
- **THEN** 必须使用完全覆写模式
- **AND** 只保留最新一次的阻塞信息

### Requirement: 精简取证规范

系统必须限制 Playwright 取证数据体积，防止上下文撑爆。

#### Scenario: DOM 取证精简

- **WHEN** test-agent 执行现场取证
- **THEN** 严禁保存完整 HTML
- **AND** 仅允许提取以下三项：
  1. 最后抛出异常的 10 行 Traceback
  2. Playwright 提取的 Accessibility Tree（仅限关键节点）
  3. 最后 3 个 Network 请求的状态码

### Requirement: 微提交保护（Micro-Commits）

系统必须在代码修改前创建保护点，确保可回滚。

#### Scenario: 测试失败回滚保护

- **WHEN** Master Agent 收到 `[REQ_DEV]` 标签（测试失败需重写）
- **THEN** 必须先执行 `git stash` 或生成临时 commit
- **AND** commit 消息格式为 `WIP: pre-fix state before retry #N`
- **AND** 确保随时可以回滚到修改前的稳定状态

### Requirement: Memory MCP 结构化写入

系统必须在 PR 合并后以结构化格式写入知识库。

#### Scenario: PR 合并后写入

- **WHEN** 阶段 7（PR 合并）成功完成
- **THEN** Master Agent 必须提炼 `test_report.md` 中的有效变更
- **AND** 以 JSON 格式写入 Memory MCP

#### Scenario: 写入契约格式

```json
{
  "tag": "[REWARDS_DOM]",
  "target": "Search Button",
  "old_selector": "#sb_form_go",
  "new_selector": "#sb_form_q",
  "trigger_date": "202x-xx-xx",
  "anti_bot_notes": "若遇图形验证码，需等待 5 秒"
}
```

### Requirement: 挂起任务恢复机制

系统必须定义挂起任务的标准恢复流程。

#### Scenario: 缺乏 DOM 结构

- **WHEN** Master Agent 读取 `blocked_reason.md`
- **AND** 原因类型为"缺乏新 DOM 结构"
- **THEN** Master Agent 调用 test-agent 单独执行 Playwright 嗅探操作
- **AND** 携新数据重新唤醒 dev-agent

#### Scenario: 核心逻辑无法实现

- **WHEN** Master Agent 读取 `blocked_reason.md`
- **AND** 原因类型为"核心逻辑无法实现"
- **THEN** Master Agent 在终端输出阻断日志
- **AND** 停止任务流转
- **AND** 彻底交出控制权给人类

### Requirement: docs-agent 量化触发条件

系统必须将"重大功能"改为可执行的量化条件。

#### Scenario: 检测新增定义

- **WHEN** 测试全绿
- **AND** Git Diff 涉及新增 `def` 或 `class`
- **THEN** 必须路由至 `[REQ_DOCS]` 更新文档

#### Scenario: 检测配置变更

- **WHEN** 测试全绿
- **AND** Git Diff 涉及配置文件（如 `.env.example`）
- **THEN** 必须路由至 `[REQ_DOCS]` 更新文档

#### Scenario: 跳过文档更新

- **WHEN** 测试全绿
- **AND** Git Diff 不满足上述条件
- **THEN** 跳过 `[REQ_DOCS]` 阶段
- **AND** 直接创建 PR

---

## MODIFIED Requirements

### Requirement: current_task.md 元数据结构

`current_task.md` 必须包含以下元数据字段：

```yaml
---
task_id: <唯一ID>
created_at: <时间戳>
type: dev | test | docs
dev_retry_count: <当前重试次数，默认 0>
max_retries: <最大重试次数，默认 3>
status: pending | in_progress | completed | blocked
---
```

### Requirement: 全局 Rule 熔断器规则

`project_rules.md` 必须新增熔断器规则：

```markdown
## 6. 熔断器规则

当 Master Agent 路由任务时：
- 若 `dev_retry_count` 达到 `max_retries`
- 禁止流转给 dev-agent
- 必须触发挂起并通知人类开发者
```

---

## REMOVED Requirements

无移除的需求。
