# 规则分层优化 Spec

## Why

当前规则结构存在"上下文膨胀"和"职责越权"问题：
- `project_rules.md` 包含底层 OS 操作命令（如 `Move-Item`），对所有 Agent 广播造成 Token 浪费
- 通用操作规范与项目特定协议混淆，导致高权限操作对低权限 Agent 产生"注意力干扰"
- User Rules 措辞较软，约束力不足

## What Changes

- **移除** `project_rules.md` 中的 Section 0.5（强制检查点）
- **新增** `project_rules.md` 顶部的"系统最高指令"硬链接声明
- **新增** `dev-execution/SKILL.md` 差异化前置检查（文件操作 + 环境依赖）
- **新增** `test-execution/SKILL.md` 差异化前置检查（Playwright 进程安全 + 测试目录隔离）
- **新增** `docs-execution/SKILL.md` 差异化前置检查（只读约束）

## Impact

- Affected specs: 多智能体协作协议
- Affected code: 
  - `.trae/rules/project_rules.md`
  - `.trae/skills/dev-execution/SKILL.md`
  - `.trae/skills/test-execution/SKILL.md`
  - `.trae/skills/docs-execution/SKILL.md`

## ADDED Requirements

### Requirement: 三层架构职责分离

系统 SHALL 实现三层规则架构，各层职责明确：

| 层级 | 职责 | 内容 |
|------|------|------|
| User Rules | 管理身份 | 通用操作规范（环境安全、文件操作） |
| Project Rules | 管理流转 | 项目特定约束（状态机、路由标签） |
| Skills | 管理动作 | 详细执行流程（前置检查、操作步骤） |

#### Scenario: Agent 执行操作前检查

- **WHEN** Agent 执行任何物理动作（读写文件、执行终端命令）
- **THEN** 必须遵守 User Rules 中的环境安全与文件操作规范

### Requirement: Skill 前置检查差异化定制

每个 Skill SHALL 根据其 Agent 的 MCP 权限矩阵定制前置检查清单。

#### Scenario: dev-execution 前置检查

- **WHEN** dev-agent 执行代码修改任务
- **THEN** 必须确认：
  - 文件移动使用 `Move-Item` 命令
  - 批量删除使用 `Remove-Item` 命令
  - 禁止自行安装依赖，发现缺失时输出 `[BLOCK_NEED_MASTER]`

#### Scenario: test-execution 前置检查

- **WHEN** test-agent 执行测试任务
- **THEN** 必须确认：
  - Playwright 进程安全（每次运行后调用 `page.close()`）
  - 测试目录隔离（绝不修改 `src/` 目录）

#### Scenario: docs-execution 前置检查

- **WHEN** docs-agent 执行文档更新任务
- **THEN** 必须确认：
  - 只修改 `docs/` 和 `.trae/documents/` 目录
  - 禁止修改业务代码

### Requirement: 环境异常对接状态机闭环

当 Agent 发现环境需要安装新依赖时，系统 SHALL 触发阻断协议：

#### Scenario: 依赖缺失阻断

- **WHEN** Agent 发现代码运行缺少第三方依赖库
- **THEN** 
  - 绝对禁止自行执行 `pip install`
  - 立刻终止当前任务
  - 输出 `[BLOCK_NEED_MASTER]` 标签
  - 在 `.trae/blocked_reason.md` 中说明"缺失依赖: XXX，需人工介入安装"

## MODIFIED Requirements

### Requirement: project_rules.md 精简形态

`project_rules.md` SHALL 只包含项目特定约束：

1. 系统最高指令（硬链接声明）
2. Master 路由格式强制校验（Section 0）
3. 多智能体协作协议（Section 1-4）

## REMOVED Requirements

### Requirement: Section 0.5 强制检查点

**Reason**: 底层 OS 操作命令不应在全局总线中广播，应下沉到对应 Skill

**Migration**: 检查清单按 Agent 权限矩阵分散到各 Skill 的前置检查中
