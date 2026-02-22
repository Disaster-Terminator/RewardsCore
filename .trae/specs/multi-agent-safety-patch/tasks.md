# Tasks

- [x] Task 1: 重构全局 Rule（project_rules.md）
  - [x] SubTask 1.1: 新增熔断器规则章节
  - [x] SubTask 1.2: 定义重试次数检查流程
  - [x] SubTask 1.3: 定义挂起通知机制

- [x] Task 2: 更新媒介文件模板
  - [x] SubTask 2.1: 更新 current_task.md 模板（新增 dev_retry_count、max_retries、status 字段）
  - [x] SubTask 2.2: 更新 test_report.md 模板（精简取证格式）
  - [x] SubTask 2.3: 更新 blocked_reason.md 模板（新增原因类型分类）

- [x] Task 3: 重构 test-execution Skill
  - [x] SubTask 3.1: 新增覆写策略约束
  - [x] SubTask 3.2: 新增精简取证规范（Traceback 10 行 + Accessibility Tree + 3 个 Network 请求）
  - [x] SubTask 3.3: 更新输出格式规范

- [x] Task 4: 重构 dev-execution Skill
  - [x] SubTask 4.1: 新增重试计数检查逻辑
  - [x] SubTask 4.2: 新增重试次数超限处理流程
  - [x] SubTask 4.3: 更新状态标签输出规则

- [x] Task 5: 重构 master-execution Skill
  - [x] SubTask 5.1: 新增微提交保护流程（git stash / WIP commit）
  - [x] SubTask 5.2: 新增重试计数递增逻辑
  - [x] SubTask 5.3: 新增熔断器检查逻辑
  - [x] SubTask 5.4: 新增 Memory MCP 结构化写入契约
  - [x] SubTask 5.5: 新增 docs-agent 量化触发条件检测

- [x] Task 6: 创建 master-recovery Skill
  - [x] SubTask 6.1: 定义触发条件（读取 blocked_reason.md）
  - [x] SubTask 6.2: 定义原因类型判断逻辑
  - [x] SubTask 6.3: 定义 DOM 嗅探恢复流程
  - [x] SubTask 6.4: 定义核心逻辑阻断流程

- [x] Task 7: 更新 test-agent 配置
  - [x] SubTask 7.1: 新增取证规范约束（禁止完整 HTML）
  - [x] SubTask 7.2: 新增覆写策略约束

- [x] Task 8: 更新 master.md 配置
  - [x] SubTask 8.1: 新增熔断器检查职责
  - [x] SubTask 8.2: 新增微提交保护职责
  - [x] SubTask 8.3: 新增 master-recovery skill 引用

# Task Dependencies

- [Task 2] 依赖 [Task 1]：媒介文件模板需要全局 Rule 的熔断器定义
- [Task 3] 依赖 [Task 2]：test-execution 需要新的 test_report.md 模板
- [Task 4] 依赖 [Task 2]：dev-execution 需要新的 current_task.md 模板
- [Task 5] 依赖 [Task 1, Task 2]：master-execution 需要熔断器规则和媒介文件模板
- [Task 6] 依赖 [Task 2]：master-recovery 需要新的 blocked_reason.md 模板
- [Task 7] 依赖 [Task 3]：test-agent 配置需要引用 test-execution 的约束
- [Task 8] 依赖 [Task 5, Task 6]：master.md 需要引用新的 skill

# Parallelizable Tasks

- [Task 3, Task 4] 可并行执行（test-execution 和 dev-execution 无直接依赖）
- [Task 7, Task 8] 可并行执行（test-agent 和 master 配置无直接依赖）
