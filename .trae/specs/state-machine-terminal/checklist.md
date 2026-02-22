# Checklist

## 状态机终止标签

- [x] project_rules.md 状态标签字典已新增 [TASK_DONE]
- [x] [TASK_DONE] 语义已定义（任务完成，停止流转）
- [x] [TASK_DONE] 响应动作已定义（无动作，等待用户）
- [x] Master Watchdog 协议已更新为 v2.0（5 标签）

## master.md 指针引用架构

- [x] master.md 中重复的 Watchdog 规则已删除
- [x] 指针引用已新增（必须服从 project_rules.md）
- [x] 约束已新增（无权发明新标签）
- [x] 格式对齐要求已新增

## Memory MCP 同步归档

- [x] pr-review/SKILL.md 已新增"审查闭环与知识归档流程"
- [x] 归档触发条件已定义（所有审查问题已解决）
- [x] 归档执行步骤已定义（提取 → 写入 → 输出 [TASK_DONE]）
- [x] 与 PR 合并流程的绑定关系已明确

## 截图目录物理规范

- [x] test-execution/SKILL.md 已新增"现场取证物理规范"
- [x] 环境准备命令已定义（mkdir -p logs/screenshots）
- [x] 执行序列已定义（环境准备 → 截图 → 进程释放 → 报告覆写）
- [x] 禁止跳过约束已明确

## 路由决策树固化

- [x] master-execution/SKILL.md 已新增"路由决策树 (Test Success)"
- [x] 人工强制覆写优先级已定义（最高优先级）
- [x] 系统静态检测命令序列已定义
- [x] 默认放行逻辑已定义

## Master Watchdog v2.0 协议

- [x] 协议版本已更新为 v2.0
- [x] 标签字典已扩展为 5 个
- [x] 格式示范已新增（正确/错误示例）
- [x] 绝对约束已明确

## 整体验证

- [x] [TASK_DONE] 标签在所有相关文件中一致
- [x] master.md 与 project_rules.md 无重复定义
- [x] 状态机闭环完整（有终止状态）
- [x] 所有新增协议不破坏现有三层控制流架构
