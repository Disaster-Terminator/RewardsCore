# Phase 1: 基础设施与数据设置 - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

建立解耦的 E2E 测试框架，包括 pytest-asyncio 框架、可重用 fixtures、测试数据管理和环境检测机制。交付可复用的基础设施，使后续测试模块能快速开发。

**范围包括：**
- `tests/e2e/` 目录结构和基础文件
- pytest 配置（标记：smoke, e2e, slow, requires_login, no_login）
- Playwright 集成和浏览器启动配置
- 基础 fixtures（每测试独立上下文，自动清理）
- 失败时自动截图和日志捕获
- 环境验证 smoke 测试
- 测试数据管理和账户凭证模板
- CI 友好的环境检测和跳过逻辑

**范围不包含：**
- 实际的业务测试（登录、搜索、任务）— 属于 Phase 2-5
- CI/CD 工作流配置 — Phase 6
- 真实测试账户的创建 — 需要用户提供
- 高级 fixtures（如 `admin_logged_in_page` 的完整实现）— 在 Phase 2-5 演进

</domain>

<decisions>
## 测试配置管理

### Config Override 策略
- **D-01:** 采用混合模式 — 基础配置继承主应用的 `ConfigManager()`，E2E 使用环境变量覆盖特定键
- **D-02:** 使用 `E2E_*` 环境变量命名空间，避免与主应用 `MS_REWARDS_*` 冲突
- **D-03:** E2E 默认覆盖值包括：
  - `search.desktop_count = E2E_SEARCH_COUNT (default: 2)`
  - `browser.headless = E2E_HEADLESS (default: false for local, true for CI)`
  - `task_system.enabled = False`
  - `scheduler.enabled = False`
  - `notification.enabled = False`
  - `diagnosis.enabled = True`

---

## 失败截图与诊断机制

### 触发方式
- **D-04:** 采用测试内捕获（try/except），不依赖 pytest 同步钩子
- **D-05:** 提供 `capture_failure_screenshot(page, test_name)` helper 函数，封装截图、DOM 快照、控制台日志

### 存储结构
- **D-06:** 按运行实例组织：`logs/e2e/run_<YYYYMMDD_HHMMSS>/screenshots/`
- **D-07:** 文件名格式：`<pytest_node_id>_<worker_id>.<ext>`（如 `test_login_flow_gw0.png`）
- **D-08:** 轮转策略：保留最近 10 次运行，每次 pytest 结束时清理过期运行

### 捕获内容
- **D-09:** 必捕获：全页面截图（full_page=True）
- **D-10:** 必捕获：DOM 快照（`page.content()`）保存为 `.html`
- **D-11:** 可选：控制台日志（通过 `page.on("console")` 监听并保存为 `.json`）

---

## 测试数据管理

### 数据格式策略（混合）
- **D-12:** 搜索词：纯文本（`search_terms.txt`，每行一个词）
- **D-13:** 账户元数据、预期验证规则：YAML（`.yaml`），可读性强，支持注释
- **D-14:** 复杂场景数据：Python 模块（`.py`），返回字典，类型安全

### 目录结构（混合）
- **D-15:** `tests/e2e/data/common/` — 共享数据（如 `search_terms.txt`, `expected_results.yaml`）
- **D-16:** `tests/e2e/data/login/` — 登录专属（`accounts.yaml`, `scenarios.py`）
- **D-17:** `tests/e2e/data/search/` — 搜索专属（`mobile_viewports.yaml`）
- **D-18:** `tests/e2e/data/tasks/` — 任务专属（`task_scenarios.py`）

---

## 环境跳过与防护

### 跳过策略（混合）
- **D-19:** 全局 autouse fixture 处理基础环境缺失（浏览器未就绪等）
- **D-20:** 自定义装饰器用于细粒度跳过：
  - `@requires_e2e_credentials` — 检查环境变量
  - `@requires_healthy_account` — 调用 `check_account_health(page)`
- **D-21:** 健康检查辅助函数：`check_account_health(page) -> dict` 返回 `{healthy, reason}`

### 生产防护
- **D-22:** `prevent_prod_pollution(page)` 守卫 — 检测到 CI + production URL 时 `raise RuntimeError`
- **D-23:** 环境检测函数：`is_ci_environment()`, `is_local_development()`, `get_environment_type()`

---

## Fixtures 优先级与命名

- **D-24:** 核心 fixtures 命名规范（session 或 function 级别）：
  - `browser`（session）— Playwright browser 实例
  - `context`（function）— 新鲜浏览器上下文
  - `page`（function）— 新鲜页面，自动清理
  - `admin_logged_in_page`（function）— 使用 storage_state 或凭据登录的页面
  - `e2e_config`（session）— 测试配置对象
- **D-25:** 所有页面相关 fixtures 必须保证 `yield` 后页面完全关闭（`assert page.is_closed()`）

---

## 项目结构约定

- **D-26:** E2E 测试目录：`tests/e2e/`，子目录：`smoke/`, `login/`, `search/`, `tasks/`, `fixtures/`, `data/`
- **D-27:** 辅助模块：`tests/e2e/helpers/`（如 `account_health.py`, `environment.py`, `screenshot.py`, `login.py`）
- **D-28:** 日志结构：
  ```
  logs/
  ├── automator.log (主应用)
  └── e2e/
      ├── run_<timestamp>/
      │   ├── screenshots/
      │   ├── dom_snapshots/
      │   └── console_logs/
      └── latest -> run_<timestamp> (符号链接)
  ```
- **D-29:** `.gitignore` 必须包含：`.env.test`, `tests/fixtures/storage_state.json`, `logs/e2e/run_*/`（但保留 artifact 上传）

---

## Claude 的裁量权

以下领域 leave 给实施者（Claude）裁量：
- **截图辅助函数的内部实现细节**（如何捕获 console logs 的过滤规则）
- **YAML schema 的具体字段定义**（账户元数据包含哪些键）
- **`conftest.py` 中的具体 pytest 钩子配置**（除已明确的决策外）
- **辅助函数的函数名和 API 设计**（在遵循原则下的具体命名）

---

## 相关待办（Fold-in）

无 pending todos 与此阶段直接相关（待办系统尚未 populated）。

---

## 范围外但被提及（Deferred）

- **并行测试资源管理详情** — worker 间临时目录隔离、文件锁策略 — 属于优化阶段，Phase 1 基础实现可满足需求
- **与主项目 ConfigManager 的深度集成选项** — 仅使用基础配置读取，不引入复杂依赖注入
- **测试数据验证 schema** — 可用 Hypothesis 在后续阶段添加属性测试

---

## 具体想法

- **参考项目现有模式** — `src/infrastructure/` 中的 `config_manager.py` 提供成熟的层级配置读取，应借鉴但保持 E2E 独立
- **CI 友好优先** — 所有环境检测和跳过逻辑必须支持无交互运行
- **错误消息清晰** — `pytest.skip()` 的 reason 应说明如何修复（如 "Set MS_REWARDS_E2E_EMAIL env var"）
- **避免过度工程** — 截图轮转、并行安全性等在 Phase 1 交付最小可行方案，后续迭代优化

---

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### E2E 框架依赖
- `pyproject.toml` — 项目依赖、pytest 配置、ruff/mypy 设置

### 主项目参考（可借鉴模式）
- `src/infrastructure/config_manager.py` — ConfigManager 实现，环境变量覆盖逻辑
- `src/infrastructure/logger.py` — 日志配置模式（可参考，但 E2E 独立）
- `CLAUDE.md` — 项目工作流、测试金字塔、验收流程

### 路线图与需求
- `.planning/ROADMAP.md` — Phase 1 目标、成功标准、交付物
- `.planning/REQUIREMENTS.md` — E2E-001, E2E-008 详细子需求
- `.planning/PROJECT.md` — 核心价值、约束、决策上下文

### 工作流模板
- `~/.claude/get-shit-done/templates/context.md` — CONTEXT.md 结构和期望格式

---

**No external design docs or ADRs exist yet — requirements fully captured in decisions above.**

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/infrastructure/config_manager.py` — ConfigManager 类提供嵌套键配置读取和环境变量支持，可作为 E2E 配置基类
- `pyproject.toml` pytest 配置 — 已有 pytest-asyncio, pytest-xdist, pytest-playwright，无需重新配置基础插件
- `src/infrastructure/logger.py` — 日志轮替和结构化日志模式，可参考但 E2E 使用独立日志目录

### Established Patterns
- **环境变量覆盖** — 主应用使用 `MS_REWARDS_*` 前缀，E2E 延续相同模式但使用 `E2E_*` 前缀
- **异步上下文管理** — 主应用广泛使用 `async with` 和 `await`，E2E 测试保持一致的 async/await 模式
- **类型注解** — 项目为 `py.typed`，E2E 代码需保持 100% 类型安全
- **目录约定** — 主应用按功能分区（`browser/`, `login/`, `search/`），E2E 可按测试类型分区（`smoke/`, `login/`, `search/`, `tasks/`）

### Integration Points
- **ConfigManager** — E2E 配置类将继承或组合主应用的 ConfigManager，通过构造函数注入
- **pytest 配置** — 需在 `pyproject.toml` 添加 `[tool.pytest.ini_options]` 覆盖 `testpaths` 以包含 `tests/e2e`
- **日志系统** — E2E 日志写入 `logs/e2e/`，与主应用 `logs/automator.log` 分离但结构相似
- **CI 集成** — Phase 6 将使用相同的 pytest 命令，确保本地与 CI 一致性

---

</code_context>

<specifics>
## Specific Ideas

- **E2E 配置类设计** — `E2ETestConfig` 包装 `ConfigManager`，通过 `_overrides` 字典优先级覆盖，保持 API 兼容 `config.get(key, default)`
- **截图命名包含 pytest node ID** — 利用 `request.node.nodeid` 自动包含参数化信息，无需手动传递测试名
- **运行实例符号链接** — `logs/e2e/latest` 指向最新运行，便于快速查看最新失败截图
- **环境检测优先级** — `check_test_environment` fixture 在 `yield` 前检查，失败立即跳过，不执行测试体
- **账户健康检查缓存** — 每个 session 缓存账户健康状态，避免每个测试重复请求
- **生产防护双重检查** — 环境检测 + URL 检查，CI 环境下访问 `rewards.microsoft.com` 直接 `raise` 而非 `skip`

---

**No specific product references or examples provided by user — implementation open to standard practices.**

</specifics>

<deferred>
## Deferred Ideas

### 并行测试资源管理优化
- Worker 间临时目录完全隔离（使用 `tmp_path_factory` 创建 per-worker 临时目录）
- 文件锁机制防止截图目录并发创建（使用 `filelock` 或原子操作）

### 深度集成选项（可选）
- 主应用 `AntiBanModule` 的随机延迟逻辑是否在 E2E 中复用？
- E2E 测试是否应使用主应用的 `StateMonitor` 来验证积分变化？
- `infrastructure/error_handler.py` 的重试装饰器是否值得提取为通用？

---

**None of these are required for Phase 1 success — can be explored in Phase 2 or later refinement.**

</deferred>

---

*Phase: 01-基础设施与数据设置*
*Context gathered: 2026-03-22*
