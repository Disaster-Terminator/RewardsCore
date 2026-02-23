# 单Agent工作流

> 本文档定义了基于 MCP 工具集的单Agent开发流程。

## 目录

- [1. 核心理念](#1-核心理念)
- [2. 验收流程](#2-验收流程)
- [3. MCP 工具配置](#3-mcp-工具配置)
- [4. Skills 调用](#4-skills-调用)
- [5. 安全边界](#5-安全边界)

---

## 1. 核心理念

| 传统模式 | MCP 模式 |
|----------|----------|
| Agent 只能读取日志 | Agent 可直接操作浏览器 |
| 验收依赖人工执行 | Playwright MCP 自动化 |
| 手动创建 PR | 用户负责 PR 创建和合并 |

**原则**：能力优先、渐进增强、安全边界（PR 创建/合并由用户负责）

---

## 2. 验收流程

### 2.1 完整验收阶段

```
阶段 1: 静态检查（ruff check + format check）
阶段 2: 单元测试（pytest unit）
阶段 3: 集成测试（pytest integration）
阶段 4: Dev 无头验收（E2E）
阶段 5: User 无头验收（E2E）
```

### 2.2 阶段定义

| 阶段 | 内容 | 命令 | 通过条件 |
|------|------|------|----------|
| 1. 静态检查 | ruff + 格式 | `ruff check . && ruff format --check .` | 无错误 |
| 2. 单元测试 | pytest unit | `pytest tests/unit/ -v` | 全部通过 |
| 3. 集成测试 | pytest integration | `pytest tests/integration/ -v` | 全部通过 |
| 4. Dev 无头 | E2E 验收 | `rscore --dev --headless` 或降级 | 退出码 0 |
| 5. User 无头 | E2E 验收 | `rscore --user --headless` 或降级 | 无严重问题 |

### 2.3 E2E 降级策略

```bash
# 步骤1：尝试 rscore（需要 pip install -e .）
rscore --dev --headless

# 步骤2：如果 rscore 不可用，降级到 main.py
python main.py --dev --headless
```

### 2.4 可选有头验收

非标准流程，用户手动执行观察 UI：

```bash
rscore --dev  # 可视化模式（优先）
python main.py --dev  # 降级方案
```

### 2.5 PR 创建与合并

| 操作 | 执行者 | 说明 |
|------|--------|------|
| 创建 PR | 用户 | Agent 不自动创建 |
| 合并 PR | 用户 | Agent 不自动合并 |

验收通过后，Agent 通知用户创建 PR。

---

## 3. MCP 工具配置

### 3.1 Memory MCP（9个）

| 工具 | 用途 |
|------|------|
| read_graph | 读取知识图谱 |
| search_nodes | 搜索节点 |
| open_nodes | 打开节点 |
| create_entities | 创建实体（知识归档） |
| create_relations | 创建关系 |
| add_observations | 添加观察 |
| delete_entities | 删除实体 |
| delete_observations | 删除观察 |
| delete_relations | 删除关系 |

### 3.2 GitHub MCP（14个）

#### 只读工具（9个）

| 工具 | 用途 |
|------|------|
| get_file_contents | 获取文件内容 |
| search_code | 搜索代码 |
| get_pull_request | 获取 PR 详情 |
| get_pull_request_files | 获取 PR 文件列表 |
| get_pull_request_status | 获取 PR CI 状态 |
| get_pull_request_comments | 获取 PR 评论 |
| get_pull_request_reviews | 获取 PR 审查 |
| list_pull_requests | 列出 PR |
| list_commits | 列出提交 |

#### 写入工具（5个）

| 工具 | 用途 |
|------|------|
| create_or_update_file | 创建/更新文件 |
| push_files | 推送多文件 |
| create_branch | 创建分支 |
| create_pull_request | 创建 PR |
| merge_pull_request | 合并 PR |

### 3.3 Playwright MCP（16个）

#### 基础导航（6个）

| 工具 | 用途 |
|------|------|
| playwright_navigate | 导航 |
| playwright_click | 点击 |
| playwright_fill | 填充 |
| playwright_select | 选择 |
| playwright_hover | 悬停 |
| playwright_press_key | 按键 |

#### 页面控制（4个）

| 工具 | 用途 |
|------|------|
| playwright_screenshot | 截图 |
| playwright_close | 关闭页面 |
| playwright_go_back | 后退 |
| playwright_go_forward | 前进 |

#### 内容获取（4个）

| 工具 | 用途 |
|------|------|
| playwright_get_visible_text | 获取文本 |
| playwright_get_visible_html | 获取 HTML（仅精简取证） |
| playwright_console_logs | 控制台日志 |
| playwright_evaluate | 执行 JS |

#### API 测试（2个）

| 工具 | 用途 |
|------|------|
| playwright_get | GET 请求 |
| playwright_post | POST 请求 |

---

## 4. Skills 调用

| Skill | 时机 | 说明 |
|-------|------|------|
| `e2e-acceptance` | 阶段 4-5 | E2E 无头验收，Playwright MCP 监控 |
| `fetch-reviews` | PR 创建后 | 获取 AI 审查评论 |

### 4.1 e2e-acceptance

调用时机：静态检查、单元测试、集成测试通过后

功能：

- 执行 Dev 无头验收
- 执行 User 无头验收
- 使用 Playwright MCP 监控页面状态
- 异常时进行精简取证

### 4.2 fetch-reviews

调用时机：用户创建 PR 后

功能：

- 获取 Sourcery/Copilot/Qodo 评论
- 分析评论类型
- 报告给用户

---

## 5. 子Agent调用

Solo Coder 可以通过调用子Agent实现并行开发。子Agent是可选的并行工具，不是必须的协作流程。

### 5.1 子Agent列表

| Agent | 职责 | 定义文件 |
|-------|------|----------|
| `dev-agent` | 代码修改与局部验证 | `.trae/agents/dev-agent.md` |
| `test-agent` | 测试执行与E2E验收 | `.trae/agents/test-agent.md` |
| `docs-agent` | 文档更新 | `.trae/agents/docs-agent.md` |

### 5.2 调用方式

| Agent | 何时调用 |
|-------|----------|
| `dev-agent` | 需要独立的代码修改会话时 |
| `test-agent` | 需要独立的测试验证会话时 |
| `docs-agent` | 需要独立的文档更新会话时 |

### 5.3 并行开发示例

```
Solo Coder
    │
    ├─► dev-agent: 修改模块A
    │
    ├─► dev-agent: 修改模块B（并行）
    │
    └─► test-agent: 运行测试（并行）
```

### 5.4 子Agent特点

- **无状态路由**：不使用状态标签，由用户/Solo Coder直接调用
- **独立运行**：不依赖通信媒介文件
- **MCP配置**：与归档版本相同，用户无需重新配置

---

## 6. 安全边界

| 自主区 | 用户确认区 |
|--------|------------|
| 读取/写入文件 | 创建 PR |
| 运行测试 | 合并 PR |
| 浏览器操作 | 删除远程分支 |
| `git add/commit/push` | 暴露 secrets |
| `git commit --amend`（未 push） | |

---

## 6. 环境诊断

如果命令执行失败，先检查环境：

```bash
pip show rewards-core  # 检查是否安装
```

---

## 7. 命令行参数

| 参数 | 搜索次数 | 调度器 | 用途 |
|------|----------|--------|------|
| 默认 | 20 | ✅ 启用 | 生产环境 |
| `--user` | 3 | ❌ 禁用 | 稳定性测试 |
| `--dev` | 2 | ❌ 禁用 | 快速调试 |
| `--headless` | - | - | 无头模式 |

---

*最后更新：2026-02-23*
