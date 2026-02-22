# Checklist

## 全局 Rule（project_rules.md）

- [x] 熔断器规则章节已新增
- [x] 重试次数检查流程已定义
- [x] 挂起通知机制已定义
- [x] 熔断器规则与 Master Agent 配置一致

## 媒介文件模板

- [x] current_task.md 模板已新增 dev_retry_count 字段
- [x] current_task.md 模板已新增 max_retries 字段
- [x] current_task.md 模板已新增 status 字段
- [x] test_report.md 模板已更新精简取证格式
- [x] blocked_reason.md 模板已新增原因类型分类

## test-execution Skill

- [x] 覆写策略约束已新增（禁止追加写入）
- [x] 精简取证规范已新增（Traceback 10 行限制）
- [x] 精简取证规范已新增（Accessibility Tree 关键节点）
- [x] 精简取证规范已新增（3 个 Network 请求状态码）
- [x] 禁止保存完整 HTML 的约束已新增
- [x] 输出格式规范已更新

## dev-execution Skill

- [x] 重试计数检查逻辑已新增
- [x] 重试次数超限处理流程已新增
- [x] 状态标签输出规则已更新（包含熔断器触发）

## master-execution Skill

- [x] 微提交保护流程已新增（git stash / WIP commit）
- [x] 重试计数递增逻辑已新增
- [x] 熔断器检查逻辑已新增
- [x] Memory MCP 结构化写入契约已新增
- [x] docs-agent 量化触发条件检测已新增（新增 def/class）
- [x] docs-agent 量化触发条件检测已新增（配置文件变更）

## master-recovery Skill

- [x] 触发条件已定义（读取 blocked_reason.md）
- [x] 原因类型判断逻辑已定义
- [x] DOM 嗅探恢复流程已定义
- [x] 核心逻辑阻断流程已定义
- [x] 文件已创建在正确路径

## test-agent 配置

- [x] 取证规范约束已新增（禁止完整 HTML）
- [x] 覆写策略约束已新增

## master.md 配置

- [x] 熔断器检查职责已新增
- [x] 微提交保护职责已新增
- [x] master-recovery skill 引用已新增

## 整体验证

- [x] 熔断器机制在所有相关文件中一致
- [x] 覆写策略在所有相关文件中一致
- [x] 精简取证规范在所有相关文件中一致
- [x] 微提交保护流程完整可执行
- [x] 挂起恢复机制完整可执行
- [x] docs-agent 触发条件可量化执行
