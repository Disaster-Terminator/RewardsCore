# 多智能体框架工程化闭环补丁 Spec

## Why

框架分析报告显示工程化抽象已达**生产级可用标准**，但第六部分（潜在问题与建议）指出四个遗留缺陷需要确定性修复协议：

1. **Memory MCP 写入时机模糊**：PR 合并后缺乏结构化归档流程
2. **docs-agent 触发条件不够精确**：Git Diff 校验逻辑需细化
3. **Playwright 取证缺乏物理落盘**：截图保存路径规范缺失
4. **Master Agent 缺乏自我校验**：可能输出错误格式的状态标签

## What Changes

### 新增确定性协议

1. **Memory MCP 结构化归档协议**：PR 合并后强制写入知识库
2. **docs-agent 确定性触发算法**：基于 Git Diff 的静态分析指令
3. **Playwright 现场取证落盘规范**：截图保存路径 + Markdown 注入
4. **Master Watchdog 自我校验**：状态标签格式强制校验

### 受影响文件

- `.trae/rules/project_rules.md`（新增 Master Watchdog 协议）
- `.trae/skills/master-execution/SKILL.md`（新增 Memory 归档流程）
- `.trae/skills/test-execution/SKILL.md`（新增截图落盘规范）

## Impact

- 受影响的 specs：`enhance-multi-agent-framework`, `multi-agent-safety-patch`
- 受影响的代码：无业务代码变更，仅配置文件增强

---

## ADDED Requirements

### Requirement: Memory MCP 结构化归档协议

系统必须在 PR 合并后执行结构化知识归档。

#### Scenario: PR 合并后触发归档

- **WHEN** PR 状态变为 `Merged`
- **AND** 当前分支准备切回 `main` 之前
- **THEN** Master Agent 必须提取 `current_task.md` 的最终状态
- **AND** 调用 Memory MCP 执行结构化写入

#### Scenario: 写入契约格式

写入内容必须符合以下 JSON Schema：

```json
{
  "entity": "Rewards_Target_Node",
  "tags": ["DOM_Rule", "Anti_Bot"],
  "content": {
    "task_id": "req-001",
    "target_element": "Search Input Box",
    "effective_locator": "input#sb_form_q",
    "obsolete_locator": "input#sb_form_go",
    "bypassing_strategy": "等待 3 秒以规避动态 DOM 渲染",
    "update_date": "202x-xx-xx"
  }
}
```

### Requirement: docs-agent 确定性触发算法

系统必须将"重大功能"转化为 AI 可执行的静态分析指令。

#### Scenario: 接口级变更触发

- **WHEN** 执行 `git diff HEAD~1`
- **AND** 新增内容包含正则表达式 `^\+\s*(def|class)\s+`
- **THEN** 必须输出 `[REQ_DOCS]`

#### Scenario: 配置级变更触发

- **WHEN** 变更文件列表中包含以下任一文件：
  - `.env.example`
  - `config.yaml`
  - `requirements.txt`
  - `pyproject.toml`
- **THEN** 必须输出 `[REQ_DOCS]`

#### Scenario: 依赖级变更触发

- **WHEN** 引入了新的第三方库
- **THEN** 必须输出 `[REQ_DOCS]`

#### Scenario: 跳过文档更新

- **WHEN** 不满足上述任一条件
- **THEN** 跳过 `[REQ_DOCS]`
- **AND** 直接进入 PR 创建阶段

### Requirement: Playwright 现场取证落盘规范

系统必须在异常捕获时执行物理落盘。

#### Scenario: 异常截图落盘

- **WHEN** test-agent 捕获异常
- **THEN** 必须立即执行：
  ```
  page.screenshot(path=f"logs/screenshots/{task_id}_crash.png", full_page=True)
  ```

#### Scenario: Markdown 注入图片路径

- **WHEN** 覆写 `.trae/test_report.md`
- **THEN** 必须在【精简取证】模块末尾注入：
  ```markdown
  ![Crash_Site](../../logs/screenshots/{task_id}_crash.png)
  ```

#### Scenario: 防止内存泄漏

- **WHEN** 截图完成后
- **THEN** 必须立即调用 `page.close()`
- **AND** 防止无头浏览器进程残留

### Requirement: Master Watchdog 自我校验协议

系统必须在 Master Agent 输出前强制执行格式校验。

#### Scenario: 状态标签格式校验

- **WHEN** Master Agent 结束任何一次回复
- **THEN** 必须执行内部正则自检
- **AND** 最终输出必须且只能以 `[` 开头，以 `]` 结尾
- **AND** 内容严格匹配字典：`[REQ_DEV]`, `[REQ_TEST]`, `[REQ_DOCS]`, `[BLOCK_NEED_MASTER]`

#### Scenario: 禁止多余文本

- **WHEN** Master Agent 输出状态标签
- **THEN** 禁止在标签后附带任何多余的解释性文本
- **AND** 示例违法输出：`现在我将调用 test-agent：[REQ_TEST]`
- **AND** 示例合法输出：`[REQ_TEST]`

---

## MODIFIED Requirements

### Requirement: project_rules.md 结构

`project_rules.md` 必须在最顶端新增 Master Watchdog 协议：

```markdown
## 0. Master 路由格式强制校验

作为 Master Agent，你在结束任何一次回复前，必须执行内部正则自检。

你的最终输出**必须且只能**以 `[` 开头，以 `]` 结尾，且内容严格匹配字典 `[REQ_DEV]`, `[REQ_TEST]`, `[REQ_DOCS]`, `[BLOCK_NEED_MASTER]` 之一。

禁止在标签后附带任何多余的解释性文本。
```

### Requirement: master-execution Skill 结构

`master-execution/SKILL.md` 必须新增 Memory MCP 归档流程：

```markdown
## Memory MCP 归档流程

### 触发时机

PR 状态变为 `Merged` 后，切回 `main` 分支前。

### 执行步骤

1. 提取 `current_task.md` 的最终状态
2. 构建结构化 JSON 实体
3. 调用 `create_entities` 写入 Memory MCP
```

### Requirement: test-execution Skill 结构

`test-execution/SKILL.md` 必须新增截图落盘规范：

```markdown
## 截图落盘规范

### 执行路径

1. 异常捕获后，立即执行截图
2. 保存路径：`logs/screenshots/{task_id}_crash.png`
3. 在 test_report.md 中注入图片路径
4. 立即调用 `page.close()` 防止内存泄漏
```

---

## REMOVED Requirements

无移除的需求。
