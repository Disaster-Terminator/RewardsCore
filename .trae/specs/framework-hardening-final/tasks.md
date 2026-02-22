# Tasks

- [x] Task 1: 新增 Master Watchdog 自我校验协议
  - [x] SubTask 1.1: 在 project_rules.md 最顶端新增"Master 路由格式强制校验"章节
  - [x] SubTask 1.2: 定义状态标签格式校验规则（以 `[` 开头，以 `]` 结尾）
  - [x] SubTask 1.3: 定义禁止多余文本规则

- [x] Task 2: 新增 Memory MCP 结构化归档流程
  - [x] SubTask 2.1: 在 master-execution/SKILL.md 新增"Memory MCP 归档流程"章节
  - [x] SubTask 2.2: 定义触发时机（PR Merged 后，切回 main 前）
  - [x] SubTask 2.3: 定义写入契约 JSON Schema
  - [x] SubTask 2.4: 定义执行步骤（提取 → 构建 → 写入）

- [x] Task 3: 细化 docs-agent 确定性触发算法
  - [x] SubTask 3.1: 在 master-execution/SKILL.md 更新 docs-agent 触发条件
  - [x] SubTask 3.2: 新增接口级变更检测（正则 `^\+\s*(def|class)\s+`）
  - [x] SubTask 3.3: 新增配置级变更检测（.env.example, config.yaml, requirements.txt, pyproject.toml）
  - [x] SubTask 3.4: 新增依赖级变更检测（新第三方库）
  - [x] SubTask 3.5: 更新检测命令示例

- [x] Task 4: 新增 Playwright 截图落盘规范
  - [x] SubTask 4.1: 在 test-execution/SKILL.md 新增"截图落盘规范"章节
  - [x] SubTask 4.2: 定义截图保存路径（`logs/screenshots/{task_id}_crash.png`）
  - [x] SubTask 4.3: 定义 Markdown 注入格式
  - [x] SubTask 4.4: 定义内存泄漏防护（`page.close()`）

- [x] Task 5: 更新 test-agent 配置
  - [x] SubTask 5.1: 在 test-agent.md 新增截图落盘约束
  - [x] SubTask 5.2: 更新精简取证规范引用

- [x] Task 6: 更新 master.md 配置
  - [x] SubTask 6.1: 新增 Memory MCP 归档职责
  - [x] SubTask 6.2: 新增 Master Watchdog 自我校验职责

# Task Dependencies

- [Task 2] 依赖 [Task 1]：Memory 归档流程需要 Master Watchdog 校验
- [Task 3] 依赖 [Task 2]：docs-agent 触发条件与 Memory 归档流程相关
- [Task 5] 依赖 [Task 4]：test-agent 配置需要引用截图落盘规范
- [Task 6] 依赖 [Task 1, Task 2]：master.md 需要引用新的职责

# Parallelizable Tasks

- [Task 3, Task 4] 可并行执行（docs-agent 触发条件和截图落盘规范无直接依赖）
- [Task 5, Task 6] 可并行执行（test-agent 和 master 配置无直接依赖）
