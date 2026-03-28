# Phase 2: 冒烟测试套件 - Context

**Gathered:** 2026-03-23
**Status:** Updated from RESEARCH (v2)
**Based on:** RESEARCH.md (2026-03-23) for implementation patterns

<domain>
## Phase Boundary

构建基础冒烟测试套件（Smoke Test Suite），提供快速（<45s CI / <30s 本地）、稳定（≥95% pass）、无外部依赖的最小验证链路。

**范围包括：**
- 浏览器/Playwright 环境健康检查
- 基本导航测试（Bing 可达性）
- 无登录依赖的最小搜索交互测试
- 性能基准测量与 flakiness 监控机制
- 失败诊断辅助（截图、日志）

**范围不包含：**
- 真实账户登录流程（属于 Phase 3）
- 认证相关 credentialed smoke 测试（独立分层）
- 积分验证或任务执行（Phase 4、5）
- CI/CD 工作流配置（Phase 6）
- 移动端或跨浏览器测试

**核心原则：**
- 快：总执行时间严格控制
- 稳：不依赖外部状态、账户健康、网络波动
- 可门禁：适合作为 PR 和合并前的快速检查
- 自诊断：失败时提供足够上下文

</domain>

<decisions>
## 冒烟测试覆盖范围

- **D-01:** 基础冒烟套件 **不包含真实登录测试**，默认只覆盖浏览器启动、导航、无账户的最小搜索交互
- **D-02:** 任何明显依赖外部状态、账户状态、网络偶发波动的测试，都不应放入这一层
- **D-03:** 认证/登录测试应作为 **单独分层**（credentialed smoke / auth smoke）在后续阶段处理
- **D-04:** Smoke suite 的目标受众是环境健康检查，不是全流程验收

---

## 性能基准严格性

- **D-05:** 本地目标：**< 30 秒**
- **D-06:** CI 宽松阈值：**< 45 秒**
- **D-07:** 超过阈值必须明确报告（warning 或 fail，具体由执行配置决定）
- **D-08:** 性能数据记录到 `logs/e2e/smoke/profile.json`，包含总耗时和各测试分布
- **D-09:** 使用 `time.perf_counter()` 进行时间测量（monotonic，避免 NTP 调整影响）
- **D-10:** 性能配置文件结构：
  ```json
  {
    "total_seconds": 23.4,
    "passed": true,
    "threshold": 30,
    "ci": false,
    "tests": [
      {"name": "test_navigate_to_bing", "seconds": 2.1}
    ],
    "session_id": 1234567890
  }
  ```

**Rationale：** Smoke 的价值是快速反馈，但 CI/本地/WSL 初始化开销存在差异，需要现实容差。

---

## Flakiness 处理策略

- **D-11:** 监控模式而非阻塞模式：记录 flakiness，超阈值告警，**默认不因为偶发波动阻断 PR**
- **D-12:** 使用文件记录运行结果，计算每个测试的 pass rate
- **D-13:** 如果某个测试持续不稳定（如 5 次运行中失败 ≥2 次），标记为 **不适合留在 smoke suite**，应移出或隔离
- **D-14:** **不采用自动重试作为默认策略**（除非某个特定测试有充分理由需要重试）
- **D-15:** 追求 **deterministic by design**，而非靠重试掩盖不稳定性

### 实施决定（基于研究）

- **D-16:** Flakiness 存储格式：**JSONL**（每行一个 JSON 条目），文件路径 `logs/e2e/flakiness.jsonl`
- **D-17:** 每个条目结构：
  ```json
  {"test": "test_basic_search_returns_results", "passed": true, "duration": 2.34, "timestamp": 1234567890.0}
  ```
- **D-18:** 分析窗口：最近 5 次运行（可配置）
- **D-19:** Flakiness 判定阈值：**pass rate < 95%**（即 ≥3 failures out of 5 runs）
- **D-20:** 集成方式：通过 `pytest_runtest_makereport` hook 记录 outcomes
- **D-21:** 报告生成：在 suite summary 中打印 flakiness 警告

**Storage Schema 示例：**
```python
# tests/e2e/smoke/helpers/flakiness.py
def get_flakiness_report(window: int = 5) -> dict:
    """返回格式: {test_name: {pass_rate, total_runs, passed, flaky}}"""
```

---

## 环境检测与跳过

- **D-22:** 采用 **两阶段检测** 策略：
  1. Stage 1: 静态检查（playwright 驱动、可执行文件）
  2. Stage 2: 动态验证（实际启动 Chromium headless）
- **D-23:** 检测函数位置：`tests/e2e/helpers/environment.py`（与 Phase 1 共享）
- **D-24:** Skip message 必须清晰且包含可操作的修复指令（如 "Run: playwright install chromium"）
- **D-25:** 检测结果缓存到 session 级别，避免重复检查
- **D-26:** 使用 `pytest.skip()` 而非 `pytest.fail()` 进行环境缺失处理（环境问题不是测试失败）

### 具体实现决定

- **D-27:** Stage 1 函数签名：`check_playwright_installed() -> Tuple[bool, str]`
  - 使用 `playwright._impl._driver.compute_driver_executable()` 验证驱动
  - 失败时返回错误详情
- **D-28:** Stage 2 函数签名：`check_browser_binary() -> Tuple[bool, str]`
  - 实际 launch Chromium headless 并立即关闭
  - 捕获并返回异常信息
- **D-29:** 环境验证测试：`tests/e2e/smoke/test_environment.py::test_smoke_environment_readiness`
  - 调用 `require_smoke_environment()` 作为第一行
  - 测试通过 simply reaches that line and completes

---

## Smokespecific Instrumentation

- **D-30:** 创建独立的 `tests/e2e/smoke/conftest.py` 保持关注点分离（不与通用 E2E fixtures 混淆）
- **D-31:** 使用 **session-scoped** 性能分析器（`smoke_profiler` fixture）记录 suite 总时长
- **D-32:** 使用 **function-scoped** `track_smoke_duration` fixture 记录每个测试的执行时间
- **D-33:** 性能数据自动保存到 `logs/e2e/smoke/profile.json`（suite 结束时）
- **D-34:** 摘要输出格式（控制台）：
  ```
  ============================================================
  SMOKE SUITE SUMMARY (CI: False)
  ============================================================
    test_navigate_to_bing: 2.134s
    test_search_input_visible: 3.456s
  ============================================================
  Total: 23.456s (threshold: 30s)
  ============================================================

  ```
- **D-35:** 摘要打印时机：`pytest_sessionfinish` 或 fixture finalizer

---

## 失败截图策略（继承 Phase 1）

- **D-36:** **仅在测试失败时截图**（failure path），不是每次运行都截图（Phase 1 D-18）
- **D-37:** 截图内容：全页面（full_page=True），保存为 PNG
- **D-38:** 同时捕获 DOM 快照（`page.content()`）保存为 HTML
- **D-39:** 可选捕获控制台日志（`page.on("console")` 监听，保存为 JSON）
- **D-40:** 不做例行启动/结束截图，保持运行轻量

---

## 账户依赖管理

- **D-41:** 基础 smoke suite **不依赖真实测试账户**（Phase 1 D-23）
- **D-42:** 任何需要账户的测试都应标记为 `@pytest.mark.requires_login` 或 `@pytest.mark.credentialed`
- **D-43:** 未来 credentialed smoke 应设计为：凭据可用且账户健康时运行，否则自动跳过

---

## 测试文件组织（基于研究）

```
tests/e2e/
├── smoke/
│   ├── __init__.py
│   ├── conftest.py                 # Smoke-specific fixtures (profiling, summary)
│   ├── helpers/
│   │   ├── __init__.py
│   │   ├── performance.py          # SmokeProfiler utilities (extractable)
│   │   └── flakiness.py            # Flakiness tracking (optional but rec'd)
│   ├── test_environment.py         # D-22, D-29 - environment validation
│   ├── test_bing_health.py         # D-30 - navigation + search input
│   ├── test_search_execution.py    # D-31 - basic search + multiple searches
│   └── test_performance_gate.py    # Optional: explicit thresholds validation
├── conftest.py                     # Phase 1: shared fixtures (browser, context, page)
└── helpers/
    ├── environment.py              # Extended with two-stage checks (D-27-D-28)
    ├── screenshot.py               # Phase 1: failure capture
    └── decorators.py               # Phase 1: requires_* decorators
```

---

## 选择器稳定性

- **D-44:** 使用标准、稳定的 selector：
  - 搜索框：`input[name='q']`（Bing 标准，不依赖 CSS 类）
  - 避免 `.b_algo` 用于关键断言（可能会变），优先使用文本或 role
- **D-45:** 使用 Playwright 的 `expect()` 进行自动等待，而非手动 `wait_for_selector`
- **D-46:** 超时设置：默认 10s，可以通过 `page.set_default_timeout(10000)` 统一设置
- **D-47:** Cookie banner 处理：使用 `get_by_role("button", name="Accept")`，添加 short timeout (2-3s)

---

## 等待策略

- **D-48:** 导航后使用 `wait_until="domcontentloaded"` 而非 `"load"`（更快，足够用于健康检查）
- **D-49:** 避免 `time.sleep()`，所有等待必须基于条件（元素出现、URL 变化、状态就绪）
- **D-50:** 对于搜索结果验证，使用 `expect(results_locator).to_have_count_greater_than(0)` 或 `.to_be_visible()`

---

## 并行策略

- **D-51:** Smoke suite **不应使用 pytest-xdist 并行执行**（单 worker 确保一致的时间和资源占用）
- **D-52:** 如果必须并行（例如 CI 资源充足），确保 flakiness 追踪使用 `filelock` 避免并发写入冲突

---

## 质量门禁

- **D-53:** 本地运行命令（推荐）：`pytest tests/e2e/smoke/ -v`
- **D-54:** 性能门禁：suite 总时长超过阈值（30s local / 45s CI）时打印 WARNING（不自动 fail，除非配置了显式 gate）
- **D-55:** Flakiness 门禁：在 PR 评论中报告持续不稳定的测试（≥2 failures in 5 runs）
- **D-56:** 通过率门禁：≥95% pass rate（即 20 次运行中最多 1 次失败）

---

## 与 Phase 1 的一致性

- **D-57:** 复用 Phase 1 的 `browser`, `context`, `page` fixtures（session-scoped browser, function-scoped context）
- **D-58:** 复用 Phase 1 的失败截图钩子（`_capture_failure_on_error`）
- **D-59:** 复用 Phase 1 的 `is_ci_environment()` 辅助函数
- **D-60:** 保持相同的日志目录结构：`logs/e2e/run_<timestamp>/`

---

## Claude 的裁量权

以下领域留给实施者自主决定（不阻塞计划但需要判断）：

- **截图辅助函数的内部实现细节**（console 日志过滤规则、DOM 快照截取时机）
- **Flakiness 检测的具体实现**（JSONL 与 single JSON 的选择、aggregation 算法优化）
- **环境检测中具体检查哪些依赖项版本**（如验证 Python 版本、pytest 插件版本）
- **`conftest.py` 的 pytest 钩子配置细节**（钩子优先级、错误处理策略）
- **性能分析的采样粒度**（是否记录每个测试的 start/end 的 precise moment，是否 include setup/teardown）
- **测试失败时的错误消息格式**（plain text vs markdown，是否包含 emoji）
- **profile.json 保存时机**（suite always vs only on failure）
- **smoke suite 是否作为 pytest marker 自动运行**（e.g., `pytest -m smoke` vs `pytest tests/e2e/smoke/`）

这些决策应在 PLAN.md 的 Task 描述中明确或注释中说明。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### E2E 框架依赖
- `pyproject.toml` — 项目依赖、pytest 配置、ruff/mypy 设置

### 路线图与需求
- `.planning/ROADMAP.md` — Phase 2 目标、成功标准、交付物
- `.planning/REQUIREMENTS.md` — E2E-002 详细子需求
- `.planning/PROJECT.md` — 核心价值、约束、整体上下文

### Phase 1 决策（可复用模式）
- `.planning/phases/01-基础设施与数据设置/01-CONTEXT.md` — 测试配置、失败截图、环境跳过、fixtures 命名等约定

### Phase 2 研究
- `.planning/phases/02-smoke-tests/02-RESEARCH.md` — 实施模式、标准栈、常见陷阱（DON'T HAND-ROLL）、代码示例

### 计划文件（待实现的具体任务）
- `.planning/phases/02-冒烟测试套件/02-01-PLAN.md` (已更新)
- `.planning/phases/02-冒烟测试套件/02-02-PLAN.md` (已更新)

### 工作流指南
- `~/.claude/get-shit-done/templates/context.md` — CONTEXT.md 结构和期望格式

---

**No external design docs or ADRs exist yet — requirements fully captured in decisions above.**

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/infrastructure/config_manager.py` — ConfigManager 嵌套配置读取和环境变量覆盖模式，E2E 配置类可借鉴
- `tests/e2e/conftest.py` (Phase 1 completed) — 基础 fixtures（browser, context, page）和失败截图钩子
- `tests/e2e/helpers/` 目录结构 — 包含 environment.py, screenshot.py, decorators.py，可直接扩展

### Established Patterns
- **环境变量命名空间** — 主应用使用 `MS_REWARDS_*` 前缀，E2E 使用 `E2E_*` 前缀（Phase 1 D-02）
- **异步测试** — 所有 E2E 测试使用 async/await；pytest-asyncio 已配置
- **类型安全** — 项目为 `py.typed`，E2E 代码需保持 100% 类型注解
- **失败诊断数据组织** — Phase 1 定义了按运行实例组织的目录结构：
  ```
  logs/e2e/run_<timestamp>/screenshots/
  logs/e2e/run_<timestamp>/dom_snapshots/
  logs/e2e/run_<timestamp>/console_logs/
  ```
- **目录分区** — E2E 按测试类型分区（smoke/, login/, search/, tasks/）
- **fixture 命名与优先级** — `browser` (session), `context` (function), `page` (function), `admin_logged_in_page` (function)

### Integration Points
- **pytest 配置** — `pyproject.toml` need `[tool.pytest.ini_options]` with markers and testpaths
- **日志系统** — E2E 日志写入 `logs/e2e/`，与主应用分离
- **CI 检测** — `is_ci_environment()` 用于性能阈值选择

---

**Phase 1 已完成，Phase 2 应直接延续其约定，不重新发明。**

</code_context>

<specifics>
## Specific Ideas

**从 RESEARCH.md 提炼的实施指引：**

- **两阶段环境检测实现**：
  ```python
  # tests/e2e/helpers/environment.py
  def check_playwright_installed() -> tuple[bool, str]:
      from playwright._impl._driver import compute_driver_executable
      compute_driver_executable()
      return True, ""

  def check_browser_binary() -> tuple[bool, str]:
      async def _check():
          async with async_playwright() as p:
              browser = await p.chromium.launch(headless=True)
              await browser.close()
              return True, ""
      return asyncio.run(_check())
  ```

- **性能分析 fixture 模板**：
  ```python
  @pytest.fixture(scope="session", autouse=True)
  def smoke_profiler(request):
      profiler = {"start": time.perf_counter(), "tests": []}
      yield profiler
      total = time.perf_counter() - profiler["start"]
      _print_summary(profiler, total)  # 包括保存 profile.json
  ```

- **环境验证测试**：
  ```python
  def test_smoke_environment_readiness():
      require_smoke_environment()
      assert True
  ```

- **Bing 搜索测试的稳健选择器策略**：
  ```python
  search_input = page.locator("input[name='q']")
  await expect(search_input).to_be_visible(timeout=10000)
  await search_input.fill("playwright python")
  await search_input.press("Enter")
  ```

- **Flakiness 追踪配置**（可选但推荐）：
  ```python
  @pytest.hookimpl(tryfirst=True, hookwrapper=True)
  def pytest_runtest_makereport(item, call):
      outcome = yield
      report = outcome.get_result()
      if report.when == "call":
          record_outcome(item.nodeid, report.passed, item._smoke_duration)
  ```

---

**No specific product references provided — standard E2E testing practices apply.**

</specifics>

<deferred>
## Deferred Ideas

### Credentialed Smoke 分层（未来）
- 独立的 `tests/e2e/credentialed/` 或 `tests/e2e/smoke_auth/`
- 依赖真实账户，但是仅当凭据可用且账户健康时运行，否则自动跳过
- 单独的质量门：`pytest tests/e2e/credentialed/ -v`

### 并行测试资源管理优化
- Worker 间临时目录完全隔离（使用 `tmp_path_factory` 创建 per-worker 临时目录）
- 文件锁机制防止 flakiness.jsonl 并发写入冲突（`filelock` 或原子操作）
- Phase 1 已标记 defer，Phase 2 可暂不实现

### 深度集成选项（可选）
- 是否复用主应用的 `AntiBanModule` 随机延迟逻辑？
- 是否使用主应用的 `HealthMonitor` 来验证性能？
- 提取通用的重试装饰器供 E2E 使用？

---

**None of these are required for Phase 2 success — keep the smoke suite lean and fast.**

</deferred>

---

## Research Backing

**This context is informed by:** `.planning/phases/02-smoke-tests/02-RESEARCH.md` (Confidence: HIGH)

**Key Research Findings:**
- Standard Stack: pytest 8.x, pytest-asyncio 0.24.x, playwright 1.49+ (no new packages)
- Architecture: Extend Phase 1 fixtures with smoke-specific instrumentation
- Don't Hand-Roll: Use Playwright's screenshot API, pytest fixtures, environment.py CI detection, JSONL for flakiness
- Common Pitfalls: Browser startup overhead (use session-scoped browser), flaky selectors (use role/text), implicit sleeps, silent skips, state leakage, internet dependency
- Performance Strategy: time.perf_counter(), session-scoped browser + function-scoped contexts, two-stage environment detection

**Implementation Guidance:** See PLAN.md files (02-01, 02-02) for detailed task breakdown.

---

*Phase: 02-冒烟测试套件*
*Context updated: 2026-03-23 (v2 — integrated RESEARCH.md, clarified decisions D-16 to D-60)*