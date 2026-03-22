# Phase 1: 基础设施与数据设置 - Discussion Log

**Date:** 2026-03-22
**Phase:** 01 - Infrastructure & Data Setup
**Areas discussed:** 4 areas (测试配置管理, 失败截图机制, 测试数据格式, 智能环境跳过)

---

## 测试配置管理

| Option | Description | Selected | Notes |
|--------|-------------|----------|-------|
| A. 完全独立 | E2E 使用独立的 config.e2e.yaml | ❌ | 维护成本高，不重用主应用逻辑 |
| **B. 继承主配置** | 直接使用 ConfigManager() | ❌ | 无隔离，E2E 可能意外影响主配置 |
| **C. 混合模式** | 继承 ConfigManager + E2E 覆盖特定键 | ✅ | **推荐**：重用成熟代码，隔离测试影响 |
| D. 你决定/其他 | - | - | - |

**User's choice:** C (给出分析后用户同意)

**Rationale:**
- `ConfigManager` 已处理环境变量、类型安全、默认值
- E2E 需要不同的运行时参数（搜索次数少、headless 默认）
- 使用 `E2E_*` 环境变量前缀，避免与主应用 `MS_REWARDS_*` 冲突

**Decisions captured:**
- **D-01:** 混合模式 — 基础配置继承 `ConfigManager()`，E2E 使用环境变量覆盖
- **D-02:** 环境变量命名空间 `E2E_*` (如 `E2E_SEARCH_COUNT`, `E2E_HEADLESS`)
- **D-03:** 默认覆盖值：`search.desktop_count=2`, `browser.headless` 根据环境, `task_system.enabled=false`, 等

---

## 失败截图机制

### 子问题 1: 触发方式

| Option | Description | Selected | Notes |
|--------|-------------|----------|-------|
| A. 异步钩子支持 | 使用 pytest-asyncio 异步钩子 | ❌ | 版本支持不确定 |
| **B. 测试内捕获** | try/except 显式调用 helper | ✅ | **推荐**：可靠、可扩展 |
| C. 插件方案 | 使用/开发 pytest 插件 | ❌ | 可能过度设计 |

**User's choice:** B (分析后用户同意)

**Rationale:**
- 不依赖 pytest 内部机制
- 可捕获更多上下文（DOM、控制台）
- 与现有计划（01-01-PLAN.md Task 1.5）一致

**Decision captured:**
- **D-04:** 采用测试内捕获，提供 `capture_failure_screenshot(page, test_name)` helper

---

### 子问题 2: 存储结构

| Option | Description | Selected | Notes |
|--------|-------------|----------|-------|
| A. 按测试名 | `logs/e2e/screenshots/test_login.png` | ❌ | 并行冲突 |
| B. 按日期 | `logs/e2e/2026-03-22/test_login.png` | ❌ | 仍需唯一化 |
| **C. 按运行实例** | `logs/e2e/run_<timestamp>/screenshots/` | ✅ | **推荐**：天然隔离 |
| D. 你决定/其他 | - | - | - |

**User's choice:** C + 轮转机制

**Rationale:**
- 每次 pytest 运行独立目录
- CI artifact 上传整个目录
- 清理策略简单（删除旧运行目录）

**Decision captured:**
- **D-06:** 存储结构 `logs/e2e/run_<YYYYMMDD_HHMMSS>/screenshots/`

---

### 子问题 3: 文件名唯一性

| Option | Description | Selected | Notes |
|--------|-------------|----------|-------|
| A. Worker ID | `test_login_gw0.png` | ❌ | 参数化测试可能冲突 |
| B. 时间戳+毫秒 | `test_login_20260322_143022_456.png` | ❌ | 可读性稍差 |
| C. UUID | `test_login_550e8400.png` | ❌ | 不可读 |
| **D. Node ID + Worker** | `test_login_flow[case1]_gw0.png` | ✅ | **推荐**：绝对唯一 |

**User's choice:** D (pytest node ID + worker ID)

**Rationale:**
- `request.node.nodeid` 包含测试路径和参数化信息
- Worker ID 来自 `PYTEST_XDIST_WORKER`
- 组合后绝对唯一，且可追溯

**Decision captured:**
- **D-07:** 文件名格式 `<node_id>_<worker_id>.<ext>`（如 `test_login_flow_gw0.png`）

---

### 子问题 4: 轮转策略

| Option | Description | Selected | Notes |
|--------|-------------|----------|-------|
| **A. 按次数保留** | 保留最近 N 次运行，自动清理 | ✅ | **推荐** |
| B. 按大小轮转 | 超过 X GB 删除最旧 | ❌ | 不精确 |
| C. 按时间轮转 | 保留最近 7-30 天 | ❌ | 天数可能过多 |
| D. 手动 | 不自动轮转 | ❌ | 易堆积 |

**User's choice:** A (按次数保留)

**Follow-up:** N = ? → **10 次**（分析后用户同意）

**Rationale:**
- 10 次 × 平均 10MB = 100MB，可接受
- 足够回溯近期 failures
- CI artifact 保留限制通常匹配

**Decision captured:**
- **D-08:** 轮转保留最近 10 次运行，每次 pytest 结束时清理

---

### 子问题 5: 捕获内容

| Content | Selected | Notes |
|---------|----------|-------|
| 全页面截图（full_page=True） | ✅ | **D-09** |
| DOM 快照（`page.content()`） | ✅ | **D-10** |
| 控制台日志（`page.on("console")`） | ✅ | **D-11**（可选但推荐） |

**Rationale:**
- 截图提供视觉上下文
- DOM 保存页面结构，便于离线分析
- 控制台日志捕获 JS 错误和网络请求

---

## 测试数据格式

### 子问题 1: 数据格式策略

| Option | Description | Selected | Notes |
|--------|-------------|----------|-------|
| A. YAML | 易读，支持注释 | ❌ | 单一格式不够灵活 |
| B. JSON | 严格，标准库 | ❌ | 可读性差 |
| C. Python 字典 | 类型安全，可含逻辑 | ❌ | 过度工程简单数据 |
| **D. 混合策略** | 按数据类型选择 | ✅ | **推荐** |

**User's choice:** D (混合策略)

**Rationale:**
- 搜索词（简单列表）→ `.txt`
- 账户元数据、预期结果（结构化）→ `.yaml`
- 复杂场景（需要函数/类）→ `.py`

**Decisions captured:**
- **D-12:** 搜索词：纯文本 `.txt`
- **D-13:** 元数据/预期结果：YAML `.yaml`
- **D-14:** 复杂场景：Python 模块 `.py`

---

### 子问题 2: 目录结构

| Option | Description | Selected | Notes |
|--------|-------------|----------|-------|
| A. 平铺 | 所有文件在 `data/` 根目录 | ❌ | 组织性差 |
| B. 按类型分组 | `accounts/`, `search_terms/`, `expected/` | ❌ | 跨类型数据访问复杂 |
| C. 按测试模块分组 | `login/`, `search/`, `tasks/` | ⚠️ | 通用数据需 `../common` |
| **D. 混合结构** | `common/` + 子目录按测试模块 | ✅ | **推荐** |

**User's choice:** D (混合结构)

**Structure:**
```
tests/e2e/data/
├── common/          # 共享（search_terms.txt, expected_results.yaml）
├── login/           # 登录专属（accounts.yaml, scenarios.py）
├── search/          # 搜索专属（mobile_viewports.yaml）
└── tasks/           # 任务专属（task_scenarios.py）
```

**Decision captured:**
- **D-15:** `tests/e2e/data/common/`
- **D-16:** `tests/e2e/data/login/`
- **D-17:** `tests/e2e/data/search/`
- **D-18:** `tests/e2e/data/tasks/`

---

## 环境跳过与防护

### 子问题: 跳过逻辑层级

| Option | Description | Selected | Notes |
|--------|-------------|----------|-------|
| A. 全局 fixture (autouse) | 每个测试自动检查 | ❌ | 过度跳过，缺乏细粒度 |
| B. 显式装饰器 | `@pytest.mark.skipif` | ❌ | 重复代码，易遗漏 |
| C. 自定义标记 | `@requires_credentials` | ❌ | 需要配合钩子 |
| **D. 混合模式** | 全局基础检查 + 装饰器细粒度 | ✅ | **推荐** |

**User's choice:** D (混合模式)

**Rationale:**
- 全局 autouse fixture 检查 Playwright 浏览器、基本环境
- 装饰器处理场景特定跳过（如需要登录的测试用 `@requires_credentials`）

**Decisions captured:**
- **D-19:** 全局 autouse fixture 处理基础环境缺失
- **D-20:** 自定义装饰器：`@requires_e2e_credentials`, `@requires_healthy_account`
- **D-21:** 健康检查辅助函数 `check_account_health(page) -> dict`

---

### 生产防护

| Mechanism | Selected | Notes |
|-----------|----------|-------|
| `prevent_prod_pollution(page)` guard | ✅ | **D-22** — CI + production URL → `raise RuntimeError` |
| 环境检测函数 | ✅ | **D-23** — `is_ci_environment()`, `is_local_development()`, `get_environment_type()` |

**Rationale:**
- 双重检查：环境 + URL
- 安全优先：CI 访问 production 直接失败而非跳过

---

## Additional Decisions (From Analysis)

- **D-24:** Fixtures 优先级：`browser` (session), `context`, `page`, `admin_logged_in_page`, `e2e_config`
- **D-25:** 所有页面 fixture 必须保证 `yield` 后 `page.is_closed()`
- **D-26:** E2E 目录结构：`tests/e2e/{smoke,login,search,tasks,fixtures,data}`
- **D-27:** 辅助模块：`tests/e2e/helpers/` 包含健康检查、环境检测、截图、登录 helper
- **D-28:** 日志目录结构（包含 `latest` 符号链接）
- **D-29:** `.gitignore` 排除 `.env.test`, `storage_state.json`, `logs/e2e/run_*/`

---

## Claude's Discretion

以下领域 leave 给实施者决定：

- 截图 helper 函数的内部实现细节（console 日志过滤规则）
- YAML schema 的具体字段（账户元数据包含哪些键）
- `conftest.py` 中 pytest 钩子配置（除已明确决策外）
- 辅助函数的函数名和 API 设计（遵循已定原则）

---

## Deferred Ideas (Out of Scope for Phase 1)

### 并行测试资源管理优化
- Worker 间临时目录完全隔离（`tmp_path_factory`）
- 文件锁防止截图目录并发创建

### 深度集成选项（可选）
- 是否复用 `AntiBanModule` 的随机延迟逻辑
- 是否使用 `StateMonitor` 验证积分变化
- 是否提取 `error_handler` 重试装饰器为通用

---

## User Corrections & Clarifications

- **用户强调：** "每个问题之前，你都要给出分析，分析之后再提问" — 后续流程必须遵守
- **截图轮转需求：** 用户补充 "C且需要轮转机制"，采纳为按运行实例 + 保留最近 N 次
- **轮转次数：** 用户选择 10 次（经过分析推荐）
- **文件名唯一性：** 用户选择 Node ID + Worker（经过分析推荐）

---

**Total decisions captured: 29 (D-01 到 D-29)**
