# Checklist

## project_rules.md 精简

- [x] Section 0.5 已移除
- [x] 顶部已添加"系统最高指令"硬链接声明
- [x] 只保留项目特定约束（Section 0-4）

## dev-execution/SKILL.md 更新

- [x] 已添加差异化前置检查（文件操作 + 环境依赖）
- [x] 已添加环境异常阻断协议（输出 `[BLOCK_NEED_MASTER]`）

## test-execution/SKILL.md 更新

- [x] 已添加差异化前置检查（Playwright 进程安全）
- [x] 已添加测试目录隔离约束

## docs-execution/SKILL.md 更新

- [x] 已添加差异化前置检查（只读约束）

## 架构验证

- [x] 三层职责分离清晰：User Rules 管身份，Project Rules 管流转，Skills 管动作
- [x] 无底层 OS 操作命令在全局总线中广播
- [x] 每个 Skill 的前置检查与其 Agent 的 MCP 权限矩阵匹配
