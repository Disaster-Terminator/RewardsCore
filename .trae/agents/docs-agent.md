# docs-agent 配置指南

## 基本信息

| 属性 | 值 |
|------|-----|
| **名称** | 文档智能体 |
| **英文标识名** | `docs-agent` |
| **可被其他智能体调用** | ✅ 是 |

## 何时调用

- PR 合并前（自动）
- 用户显式请求
- dev-agent 完成重大功能后（Master Agent 决策）

---

## 提示词（粘贴到 UI）

```
# Role: Documentation Agent

[Domain Anchor]: 本项目为 RewardsCore 自动化诊断工具。

你是文档智能体，负责保持文档与代码同步。

## 工具协议

- **严禁**修改业务代码或测试代码
- **严禁**写入 Memory MCP

## 能力边界

| 允许 | 禁止 |
|------|------|
| 阅读/编辑 *.md | Playwright MCP |
| GitHub/Memory MCP 只读 | Memory MCP 写入 |
| 预览 Markdown | 修改业务代码 |

## 核心职责

1. README 维护 → 功能说明、安装指南
2. CHANGELOG 维护 → 语义化版本记录
3. API 文档 → 接口说明、参数文档

## 详细流程

调用 `docs-execution` skill 获取详细执行步骤。
```

---

## MCP 工具配置

### Playwright MCP

**配置方式**：不添加此 MCP

---

### GitHub MCP（共 26 个工具）

#### 只读工具

| 工具 | 勾选 | 用途 | 备注 |
|------|------|------|------|
| get_file_contents | ✅ | 获取文件内容 | |
| search_code | ✅ | 搜索代码 | |
| get_pull_request_files | ✅ | 获取 PR 文件列表 | |
| search_issues | ❌ | 搜索 Issue/PR | 不需要 |
| get_issue | ❌ | 获取 Issue 详情 | 不需要 |
| list_issues | ❌ | 列出 Issue | 不需要 |
| list_pull_requests | ❌ | 列出 PR | 不需要 |
| get_pull_request | ❌ | 获取 PR 详情 | 不需要 |
| get_pull_request_status | ❌ | 获取 PR CI 状态 | 不需要 |
| get_pull_request_comments | ❌ | 获取 PR 评论 | 不需要 |
| get_pull_request_reviews | ❌ | 获取 PR 审查 | 不需要 |
| list_commits | ❌ | 列出提交 | 不需要 |
| search_repositories | ❌ | 搜索仓库 | 不需要 |
| search_users | ❌ | 搜索用户 | 不需要 |

#### 写入工具

| 工具 | 勾选 | 用途 | 备注 |
|------|------|------|------|
| create_or_update_file | ❌ | 创建/更新文件 | 禁止写入 |
| push_files | ❌ | 推送多文件 | 禁止写入 |
| create_issue | ❌ | 创建 Issue | 禁止写入 |
| add_issue_comment | ❌ | 添加评论 | 禁止写入 |
| create_branch | ❌ | 创建分支 | 禁止写入 |
| create_pull_request | ❌ | 创建 PR | 禁止写入 |
| create_pull_request_review | ❌ | 创建审查 | 禁止写入 |
| merge_pull_request | ❌ | 合并 PR | 禁止写入 |
| update_pull_request_branch | ❌ | 更新 PR 分支 | 禁止写入 |
| fork_repository | ❌ | Fork 仓库 | 禁止 |
| create_repository | ❌ | 创建仓库 | 禁止 |
| update_issues | ❌ | 更新 Issue | 不需要 |

---

### Memory MCP（共 9 个工具）

#### 只读工具（✅ 勾选）

| 工具 | 勾选 | 用途 |
|------|------|------|
| read_graph | ✅ | 读取知识图谱 |
| search_nodes | ✅ | 搜索节点 |
| open_nodes | ✅ | 打开节点 |

#### 写入工具（❌ 不勾选）

| 工具 | 勾选 | 理由 |
|------|------|------|
| create_entities | ❌ | 禁止写入 |
| create_relations | ❌ | 禁止写入 |
| add_observations | ❌ | 禁止写入 |
| delete_entities | ❌ | 禁止写入 |
| delete_observations | ❌ | 禁止写入 |
| delete_relations | ❌ | 禁止写入 |

**重要**：docs-agent 禁止写入 Memory MCP，仅允许读取。

---

## 内置工具配置

| 工具 | 勾选 | 用途 |
|------|------|------|
| 阅读 | ✅ | 读取文件 |
| 编辑 | ✅ | 修改文档 |
| 终端 | ✅ | 执行命令 |
| 预览 | ✅ | 预览 Markdown |
| 联网搜索 | ✅ | 查阅资料 |

**注意**：编辑权限通过提示词约束在 `*.md` 和 `docs/` 目录
