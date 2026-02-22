---
name: docs-execution
description: 文档执行详细流程。docs-agent 执行文档更新时调用。
---

# 文档执行详细流程

## 触发条件

- PR 合并前（自动）
- 用户显式请求
- dev-agent 完成重大功能后（Master Agent 决策）

## 核心职责

### 1. README 维护

- 功能说明
- 安装指南
- 使用命令

### 2. CHANGELOG 维护

- 按语义化版本（SemVer）记录变更
- 提取代码 Diff 生成变更说明

### 3. API 文档

- 接口说明
- 参数文档

## 输出格式（强制）

```
---
task_id: <任务ID>
status: success
---

### 文档变更清单

- `<文件路径>`: <变更说明，如：新增了代理配置参数的说明>

### 关联代码

- 关联 PR/Commit: <ID>
```

## 编辑范围约束

- **允许**：`*.md` 文件、`docs/` 目录
- **禁止**：业务代码（`src/`）、测试代码（`tests/`）
