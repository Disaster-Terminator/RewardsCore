# Checklist

## Master Watchdog 自我校验协议

- [x] project_rules.md 最顶端已新增"Master 路由格式强制校验"章节
- [x] 状态标签格式校验规则已定义（以 `[` 开头，以 `]` 结尾）
- [x] 禁止多余文本规则已定义
- [x] 合法/违法输出示例已提供

## Memory MCP 结构化归档流程

- [x] master-execution/SKILL.md 已新增"Memory MCP 归档流程"章节
- [x] 触发时机已定义（PR Merged 后，切回 main 前）
- [x] 写入契约 JSON Schema 已定义
- [x] 执行步骤已定义（提取 → 构建 → 写入）
- [x] JSON Schema 包含必要字段（entity, tags, content）

## docs-agent 确定性触发算法

- [x] master-execution/SKILL.md 已更新 docs-agent 触发条件
- [x] 接口级变更检测已新增（正则 `^\+\s*(def|class)\s+`）
- [x] 配置级变更检测已新增（.env.example, config.yaml, requirements.txt, pyproject.toml）
- [x] 依赖级变更检测已新增（新第三方库）
- [x] 检测命令示例已更新
- [x] 跳过条件已明确定义

## Playwright 截图落盘规范

- [x] test-execution/SKILL.md 已新增"截图落盘规范"章节
- [x] 截图保存路径已定义（`logs/screenshots/{task_id}_crash.png`）
- [x] Markdown 注入格式已定义
- [x] 内存泄漏防护已定义（`page.close()`）
- [x] 截图执行时机已明确（异常捕获后立即执行）

## test-agent 配置更新

- [x] test-agent.md 已新增截图落盘约束
- [x] 精简取证规范引用已更新

## master.md 配置更新

- [x] master.md 已新增 Memory MCP 归档职责
- [x] master.md 已新增 Master Watchdog 自我校验职责

## 整体验证

- [x] Master Watchdog 协议在 project_rules.md 和 master.md 中一致
- [x] Memory 归档流程在 master-execution 和 master.md 中一致
- [x] docs-agent 触发条件可量化执行（正则 + 文件列表）
- [x] 截图落盘规范在 test-execution 和 test-agent.md 中一致
- [x] 所有新增协议不破坏现有三层控制流架构
