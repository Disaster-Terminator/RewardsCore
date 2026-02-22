# 状态机闭环补全 Spec

## Why

状态机缺乏终止状态（Terminal State）是导致多智能体系统在任务末端产生幻觉、违背输出协议的根本性拓扑缺陷。当前四个标签都是路由标签，Master Agent 在完成任务后无法优雅退出。

## What Changes

### **BREAKING** 状态机拓扑补全

1. **新增终止标签**：`[TASK_DONE]` 表示任务完成，Agent 停止一切活动
2. **重构 Master Watchdog**：从 4 标签扩展到 5 标签，明确格式约束
3. **同步化 Memory 归档**：将异步触发改为同步绑定到 pr-review 流程
4. **固化执行序列**：截图目录创建、docs-agent 检测算法显式化
5. **DRY 原则**：master.md 采用指针引用 project_rules.md

### 受影响文件

- `.trae/rules/project_rules.md`（新增 [TASK_DONE] 标签 + Watchdog v2.0）
- `.trae/prompts/master.md`（指针引用架构）
- `.trae/skills/pr-review/SKILL.md`（同步 Memory 归档）
- `.trae/skills/test-execution/SKILL.md`（截图目录物理规范）
- `.trae/skills/master-execution/SKILL.md`（路由决策树固化）

## Impact

- 受影响的 specs：`enhance-multi-agent-framework`, `multi-agent-safety-patch`, `framework-hardening-final`
- 受影响的代码：无业务代码变更，仅配置文件增强

---

## ADDED Requirements

### Requirement: 状态机终止标签

系统必须提供明确的终止状态标签，以截断 Master Agent 的长程注意力机制。

#### Scenario: 任务完成输出终止标签

- **WHEN** 当前需求的所有子任务已闭环
- **OR** 已成功挂起等待人类介入
- **THEN** Master Agent 必须输出 `[TASK_DONE]`
- **AND** 输出此标签后，Agent 必须停止一切活动

#### Scenario: 终止标签语义

`[TASK_DONE]` 标签的语义：
- 当前任务链已完整执行
- 无需进一步路由
- 等待用户下一步指令

### Requirement: Master Watchdog v2.0 协议

系统必须强化 Master Agent 的输出格式约束。

#### Scenario: 五标签强制匹配

- **WHEN** Master Agent 结束回复
- **THEN** 最后一行必须且只能输出路由标签
- **AND** 标签必须严格匹配字典中的 5 个之一：
  - `[REQ_DEV]`
  - `[REQ_TEST]`
  - `[REQ_DOCS]`
  - `[BLOCK_NEED_MASTER]`
  - `[TASK_DONE]`

#### Scenario: 格式示范

```markdown
✅ 正确示范：
（前面的分析内容...）
[REQ_DEV]

❌ 错误示范：
（前面的分析内容...）
好的，我已经将任务交给了 dev-agent，标签是 [REQ_DEV]。
```

### Requirement: Memory MCP 同步归档

系统必须将 Memory 归档动作前置到同步任务流中。

#### Scenario: PR 准备合并时归档

- **WHEN** 检测到所有 AI 审查问题均已标记为 `✅ Addressed` 或被判定为可忽略
- **AND** 在通知人类进行合并之前
- **THEN** 必须执行以下同步操作：
  1. 从 `current_task.md` 和 `test_report.md` 提取核心问题
  2. 调用 Memory MCP 写入经验
  3. 输出 `[TASK_DONE]` 终止流转

### Requirement: 截图目录物理规范

系统必须在截图前确保目录存在。

#### Scenario: 现场取证执行序列

- **WHEN** 捕获测试异常
- **THEN** 必须按以下顺序执行，禁止跳过：
  1. **环境准备**：执行 `mkdir -p logs/screenshots`
  2. **截取快照**：`page.screenshot(path=f"logs/screenshots/{task_id}_crash.png", full_page=True)`
  3. **进程释放**：`page.close()`
  4. **报告覆写**：注入图片路径到 `test_report.md`

### Requirement: 路由决策树固化

系统必须明确 Master Agent 在测试成功后的决策执行树。

#### Scenario: 人工强制覆写

- **WHEN** 用户明确要求"更新文档"
- **THEN** 跳过所有检测，直接输出 `[REQ_DOCS]`

#### Scenario: 系统静态检测

- **WHEN** test-agent 返回全部测试通过
- **AND** 无人工强制指令
- **THEN** 执行以下检测：
  1. `git diff HEAD~1 --name-only` 检查配置文件
  2. `git diff HEAD~1 -U0 | grep '^\+\s*\(def\|class\)'` 检查新增函数/类
- **AND** 若有匹配，输出 `[REQ_DOCS]`

#### Scenario: 默认放行

- **WHEN** 以上条件均不满足
- **THEN** 进入 PR 创建流程，或输出 `[TASK_DONE]` 结束任务

### Requirement: DRY 原则指针引用

系统必须确立全局 Rule 的"唯一真相源"地位。

#### Scenario: master.md 指针引用

- **WHEN** Master Agent 读取配置
- **THEN** master.md 不重复定义 Watchdog 规则
- **AND** 采用指针引用：`必须绝对服从 project_rules.md 中的定义`

---

## MODIFIED Requirements

### Requirement: 状态标签字典扩展

`project_rules.md` 的状态标签字典必须新增：

| 标签 | 含义 | 触发者 | 响应动作 |
|------|------|--------|----------|
| `[TASK_DONE]` | 任务完成，等待用户指令 | Master Agent | 无动作，停止流转 |

### Requirement: master.md 架构重构

`master.md` 必须删除重复的 Watchdog 规则描述，替换为指针引用：

```markdown
# Routing Constraints

你的路由决策与状态流转**必须绝对服从** `project_rules.md` 中定义的【状态标签字典】与【强制自我校验协议】。

你无权发明新标签。每次回复结束前，必须读取 `project_rules.md` 中的规范进行格式对齐。
```

---

## REMOVED Requirements

无移除的需求。
