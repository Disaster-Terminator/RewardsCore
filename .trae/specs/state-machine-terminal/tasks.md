# Tasks

- [x] Task 1: 新增状态机终止标签 [TASK_DONE]
  - [x] SubTask 1.1: 在 project_rules.md 状态标签字典中新增 [TASK_DONE]
  - [x] SubTask 1.2: 定义 [TASK_DONE] 语义（任务完成，停止流转）
  - [x] SubTask 1.3: 更新 Master Watchdog 协议为 v2.0（5 标签）

- [x] Task 2: 重构 master.md 为指针引用架构
  - [x] SubTask 2.1: 删除 master.md 中重复的 Watchdog 规则描述
  - [x] SubTask 2.2: 新增指针引用：必须服从 project_rules.md
  - [x] SubTask 2.3: 新增约束：无权发明新标签

- [x] Task 3: 同步化 Memory MCP 归档流程
  - [x] SubTask 3.1: 在 pr-review/SKILL.md 新增"审查闭环与知识归档流程"
  - [x] SubTask 3.2: 定义归档触发条件（所有审查问题已解决）
  - [x] SubTask 3.3: 定义归档执行步骤（提取 → 写入 → 输出 [TASK_DONE]）

- [x] Task 4: 固化截图目录物理规范
  - [x] SubTask 4.1: 在 test-execution/SKILL.md 新增"现场取证物理规范"
  - [x] SubTask 4.2: 定义环境准备命令（mkdir -p logs/screenshots）
  - [x] SubTask 4.3: 定义执行序列（环境准备 → 截图 → 进程释放 → 报告覆写）

- [x] Task 5: 固化路由决策树
  - [x] SubTask 5.1: 在 master-execution/SKILL.md 新增"路由决策树 (Test Success)"
  - [x] SubTask 5.2: 定义人工强制覆写优先级
  - [x] SubTask 5.3: 定义系统静态检测命令序列
  - [x] SubTask 5.4: 定义默认放行逻辑

- [x] Task 6: 更新 project_rules.md Master Watchdog 协议
  - [x] SubTask 6.1: 更新协议版本为 v2.0
  - [x] SubTask 6.2: 扩展标签字典为 5 个
  - [x] SubTask 6.3: 新增格式示范（正确/错误示例）

# Task Dependencies

- [Task 2] 依赖 [Task 1]：master.md 指针引用需要 [TASK_DONE] 标签已定义
- [Task 3] 依赖 [Task 1]：Memory 归档输出 [TASK_DONE] 需要标签已定义
- [Task 6] 依赖 [Task 1]：Watchdog v2.0 需要 [TASK_DONE] 标签已定义

# Parallelizable Tasks

- [Task 3, Task 4, Task 5] 可并行执行（三个 Skill 文件修改无直接依赖）
- [Task 2, Task 6] 需顺序执行（Task 1 → Task 6 → Task 2）
