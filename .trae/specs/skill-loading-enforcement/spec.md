# Skill 加载与约束传递强化 Spec

## Why

当前多智能体框架存在两个致命工程缺陷：
1. **惰性求值导致的规则遗漏** - Skill 是"按需加载"，Agent 可能跳过，导致前置检查不生效
2. **粗粒度异常捕获导致的错误归因** - 降级策略只关注"最终结果"，不关注"中间过程的失败原因"

## What Changes

- **MODIFIED** `dev-agent.md` - 将物理边界约束上移到 Agent 提示词，强制 Skill 加载
- **MODIFIED** `test-agent.md` - 将物理边界约束上移到 Agent 提示词，强制 Skill 加载
- **MODIFIED** `test-execution/SKILL.md` - 增强降级策略的错误分离，注入二维错误诊断矩阵

## Impact

- Affected specs: 多智能体协作协议
- Affected code:
  - `.trae/agents/dev-agent.md`
  - `.trae/agents/test-agent.md`
  - `.trae/skills/test-execution/SKILL.md`

## ADDED Requirements

### Requirement: 物理边界约束上移

Agent 提示词 SHALL 包含物理环境前置检查，作为常驻上下文中的强制约束。

#### Scenario: dev-agent 前置检查

- **WHEN** dev-agent 被唤醒
- **THEN** 必须在执行任何终端操作前进行内部拦截校验：
  - 文件迁移：强制使用 `Move-Item`
  - 文件删除：强制使用 `Remove-Item`
  - 依赖变更：禁止自行执行 `pip install`，触发阻断协议

#### Scenario: test-agent 前置检查

- **WHEN** test-agent 被唤醒
- **THEN** 必须在执行任何操作前确认：
  - Playwright 进程安全：每次运行后调用 `page.close()`
  - 测试目录隔离：绝不修改 `src/` 目录
  - 环境依赖：禁止自行安装

### Requirement: 强制 Skill 加载

Agent 执行流程 SHALL 将 Skill 加载作为强制第一步，禁止跳过。

#### Scenario: dev-agent 执行序列

- **WHEN** dev-agent 被唤醒
- **THEN** 必须按以下顺序执行：
  1. 获取上下文：读取 `.trae/current_task.md`
  2. **强制加载 SOP**：检索并完整阅读 `.trae/skills/dev-execution/SKILL.md`
  3. 执行与验证：遵循 SOP 完成代码修改
  4. 状态流转：输出状态标签

#### Scenario: test-agent 执行序列

- **WHEN** test-agent 被唤醒
- **THEN** 必须按以下顺序执行：
  1. 获取上下文：读取 `.trae/current_task.md`
  2. **强制加载 SOP**：检索并完整阅读 `.trae/skills/test-execution/SKILL.md`
  3. 执行与验证：遵循 SOP 完成测试
  4. 状态流转：输出状态标签

### Requirement: 二维错误诊断矩阵

test-agent 执行 E2E 验收时 SHALL 使用二维错误诊断矩阵进行精准归因。

#### Scenario: rscore 入口点配置错误

- **WHEN** rscore 抛出 `ModuleNotFoundError`
- **AND** python main.py 任意结果
- **THEN** 结论为【环境问题：rscore 入口点配置错误】，触发 `[REQ_DEV]` 修复包结构

#### Scenario: 核心依赖缺失

- **WHEN** rscore 任意结果
- **AND** python main.py 抛出 `ModuleNotFoundError`
- **THEN** 结论为【环境问题：核心依赖缺失】，触发 `[BLOCK_NEED_MASTER]` 要求人类介入

#### Scenario: 业务逻辑缺陷

- **WHEN** rscore 抛出业务逻辑堆栈（如 Timeout）
- **AND** python main.py 抛出业务逻辑堆栈
- **THEN** 结论为【业务问题：逻辑实现缺陷】，执行 Playwright 现场取证，触发 `[REQ_DEV]`

#### Scenario: rscore 包装器失效

- **WHEN** rscore 任意异常
- **AND** python main.py 成功运行（Exit Code 0）
- **THEN** 结论为【配置问题：rscore 包装器失效】，触发 `[REQ_DEV]` 修复 CLI 入口

#### Scenario: 验证通过

- **WHEN** rscore 成功运行
- **THEN** 结论为【验证通过】，准备进入文档同步或完结状态

## MODIFIED Requirements

### Requirement: Agent 提示词结构

Agent 提示词 SHALL 采用以下结构：

```markdown
# Constraints（绝对严禁事项）

## 1. 物理环境前置检查（强制拦截）
[具体检查项]

## 2. 权限隔离约束
[具体约束]

# Execution & Routing (强制执行序列)

当你被唤醒时，**必须且只能**严格按以下顺序执行，禁止跳过任何一步：
1. **获取上下文**：读取 `.trae/current_task.md`
2. **强制加载 SOP**：检索并完整阅读对应 Skill
3. **执行与验证**：遵循 SOP 完成任务
4. **状态流转**：输出状态标签
```
