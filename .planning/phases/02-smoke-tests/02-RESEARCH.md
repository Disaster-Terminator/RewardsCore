# Phase 2: Smoke Test Suite - Research

**Researched:** 2026-03-23
**Domain:** Playwright + pytest-asyncio E2E smoke testing
**Confidence:** HIGH

## Summary

Phase 2 focuses on building a fast, stable, self-contained smoke test suite that validates browser/Playwright environment health and basic Bing accessibility without requiring real accounts. The research confirms that the existing Phase 1 infrastructure (fixtures, environment detection, screenshot capture) provides a solid foundation. Key recommendations include: using pytest markers for smoke categorization, implementing flakiness tracking via session-scoped storage, employing performance profiling per test, and following Playwright best practices for deterministic tests (proper wait strategies, isolated contexts, explicit timeouts).

**Primary recommendation:** Extend existing fixtures with smoke-specific helpers (performance tracking, environment pre-checks, flakiness recording) and write 5-7 focused tests covering browser launch, navigation, search input acceptance, basic search execution, and graceful skipping.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | >=8.0.0 | Test framework | Project already uses; fixtures, markers, async support |
| pytest-asyncio | >=0.24.0 | Async test support | Required for async Playwright tests; already in pyproject.toml |
| playwright | >=1.49.0 | Browser automation | Core dependency; aligned with main app |
| pytest-playwright | >=0.5.0 | Pytest integration (optional) | Provides `page` fixture alternative; but Phase 1 has custom fixtures, so optional |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-timeout | >=2.3.0 | Per-test timeout enforcement | Add to smoke tests to guarantee <30s total |
| pytest-benchmark | >=5.0.0 | Performance measurement | Alternative to custom timing; but lightweight manual timing is simpler |
| rich | >=13.0.0 | Pretty console output | For final summary display (duration metrics) |
| filelock | >=3.15.0 | Flakiness tracking file sync | If running in parallel with xdist; not needed for single-worker smoke |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytest-playwright fixture | Custom fixtures (current) | Custom gives full control over environment detection and failure capture; pytest-playwright adds abstraction but less flexible |
| pytest-timeout | Manual time tracking | Manual is simpler but doesn't auto-fail; pytest-timeout auto-fails on timeout |
| pytest-benchmark | Manual time measurement | Manual sufficient for simple profiles; benchmark adds overhead and complexity |

**Installation:**
```bash
# Core dependencies already installed via pip install -e ".[dev]"
# No additional packages required - all in dev dependencies
pip install -e ".[dev]"
```

## Architecture Patterns

### Recommended Project Structure

```
tests/e2e/
├── smoke/                      # Phase 2 deliverable
│   ├── __init__.py
│   ├── conftest.py            # Smoke-specific fixtures (performance tracking, flakiness)
│   ├── test_environment.py    # Browser launch + navigation
│   ├── test_bing_health.py    # Bing homepage + search input
│   ├── test_search_flow.py    # Basic search execution (<10s)
│   ├── test_performance.py    # Duration assertions per test
│   └── test_summary.py        # Final suite summary (durations, flakiness)
├── conftest.py                # Phase 1: shared fixtures (browser, context, page)
├── helpers/
│   ├── environment.py        # Phase 1: CI/local detection, Playwright check
│   ├── screenshot.py         # Phase 1: failure capture
│   ├── decorators.py         # Phase 1: requires credentials guard
│   └── flakiness.py          # NEW: flakiness tracking utilities
└── data/                     # Test data (search terms, etc.)
    └── common/search_terms.txt
```

### Pattern 1: Smoke-Specific Fixture Extension

**What:** Extend Phase 1's `conftest.py` with smoke-specific fixtures that add performance tracking, flakiness recording, and environment pre-checks without polluting the general E2E fixtures.

**When to use:** For smoke suite only; keep smoke concerns isolated from other E2E suites.

**Example:**
```python
# tests/e2e/smoke/conftest.py
import pytest
import time
from pathlib import Path
from tests.e2e.helpers.flakiness import record_test_result

FLAKINESS_DB = Path("logs/e2e/flakiness.json")

@pytest.fixture
async def smoke_page(page):
    """Page fixture with smoke-specific instrumentation."""
    start_time = time.perf_counter()
    yield page
    duration = time.perf_counter() - start_time

    # Record performance for summary
    record_test_result(
        test_name=page._test_name or "unknown",
        duration=duration,
        passed=page._test_passed if hasattr(page, "_test_passed") else True,
    )

@pytest.fixture(scope="session", autouse=True)
def smoke_summary(request):
    """Print summary at end of smoke suite."""
    yield
    # After all tests, print duration summary and flakiness warnings
    _print_smoke_summary()
```

**Source:** Pattern based on standard pytest fixture stacking and session-scoped teardown.

### Pattern 2: Two-Stage Environment Detection

**What:** Separate quick static pre-checks (executable paths, dependencies) from expensive browser launch validation. Fail fast with clear messages.

**When to use:** In smoke environment guard fixture to skip entire suite if Playwright not installed.

**Example:**
```python
# tests/e2e/helpers/environment.py (extend)
import shutil

def check_playwright_installed() -> tuple[bool, str]:
    """Check if Playwright browsers are installed."""
    try:
        from playwright._impl._driver import compute_driver_executable
        compute_driver_executable()
        return True, ""
    except Exception as e:
        return False, f"Playwright drivers not found: {e}"

def check_browser_binary() -> tuple[bool, str]:
    """Check if Chromium binary exists."""
    import asyncio
    from playwright.async_api import async_playwright

    async def _check():
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                await browser.close()
                return True, ""
        except Exception as e:
            return False, str(e)

    return asyncio.run(_check())

def require_smoke_environment():
    """Raise pytest.skip with actionable message if environment not ready."""
    ok, msg = check_playwright_installed()
    if not ok:
        pytest.skip(f"Playwright not installed. Run: playwright install chromium. Details: {msg}")

    ok, msg = check_browser_binary()
    if not ok:
        pytest.skip(f"Chromium not available. Run: playwright install chromium. Details: {msg}")
```

**Source:** Based on CONTEXT.md decisions D-14 through D-17.

### Pattern 3: Performance Profiling and Assertion

**What:** Time each smoke test, record total suite duration, and assert against configurable thresholds (30s local, 45s CI).

**When to use:** In smoke summary fixture and per-test duration tracking.

**Example:**
```python
# tests/e2e/smoke/helpers/performance.py
import time
import json
from pathlib import Path

class SmokeProfiler:
    def __init__(self):
        self.start_time = None
        self.test_timings = []

    def start_suite(self):
        self.start_time = time.perf_counter()

    def record_test(self, name: str, duration: float):
        self.test_timings.append({"name": name, "seconds": duration})

    def suite_duration(self) -> float:
        return time.perf_counter() - self.start_time

    def save_profile(self, path: Path):
        profile = {
            "total_seconds": self.suite_duration(),
            "passed": self.suite_duration() < (45 if is_ci_environment() else 30),
            "tests": self.test_timings,
        }
        path.write_text(json.dumps(profile, indent=2))
```

**Source:** CONTEXT.md decision D-08 specifies profile.json output.

### Anti-Patterns to Avoid

- **Don't** use large sleeps (`time.sleep(5)`). Use proper wait conditions (`page.wait_for_selector`, `page.wait_for_load_state`).
- **Don't** share browser contexts between tests. Each test must have fresh context for isolation.
- **Don't** write smoke tests that depend on real credentials. That's a separate layer (Phase 3).
- **Don't** use implicit waits. Always be explicit about what you're waiting for.
- **Don't** write flaky selectors. Prefer `data-testid` attributes or robust selectors (text, role).
- **Don't** run smoke in parallel (xdist) unless absolutely necessary. Parallel introduces resource contention and may inflate duration.
- **Don't** use `page.goto(wait_until="load")` for Bing. Use `networkidle` or `domcontentloaded` appropriately to avoid hanging.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Screenshot & diagnostic capture | Custom file management, PNG encoding | Playwright's built-in `page.screenshot()` | Simpler, reliable, handles full_page correctly |
| Console log collection | Manual event listeners | `page.on("console", handler)` — already in Phase 1 | Standard API, sufficient |
| Browser context isolation | Shared context with manual cleanup | pytest fixtures (function-scoped context) | Automatic setup/teardown, exception-safe |
| Environment detection | Hardcoded heuristics | Use CI env vars (CI, GITHUB_ACTIONS, etc.) — already in `environment.py` | De facto standard across CI systems |
| Performance timing | `datetime.now()` | `time.perf_counter()` for sub-second precision | Monotonic, not subject to NTP adjustments |
| Flakiness storage | Custom database | JSON file with append-only writes | Simple, human-readable, no concurrency needed for single-run |

**Key insight:** Smoke tests should compose existing utilities (fixtures, helpers) rather than introduce new infrastructure. Keep it minimal.

## Runtime State Inventory

*Not applicable* — Phase 2 is a greenfield test suite implementation with no runtime state or name refactoring involved.

## Common Pitfalls

### Pitfall 1: Browser Startup Overhead Blowing Duration Budget

**What goes wrong:** Smoke suite takes 45+ seconds because browser launch (~3-5s) + context creation (~1-2s) multiplied by N tests dominates runtime.

**Why it happens:** Using function-scoped browser fixture (launch per test) instead of session-scoped browser.

**How to avoid:**
- Keep browser fixture session-scoped (already done in Phase 1 `conftest.py`)
- Keep context/page function-scoped (for isolation)
- Reuse the same browser instance across all tests
- Total cost: 1 browser launch + N context/page creations

**Warning signs:** First test takes 5s, subsequent tests take 1-2s each. That's expected. If all tests take 5s, suspect shared browser cost per test.

### Pitfall 2: Flaky Selectors Causing Spurious Failures

**What goes wrong:** Tests fail intermittently because Bing DOM changed or element not appearing in time.

**Why it happens:** Using CSS selectors that are not robust; not waiting for elements; network delays.

**How to avoid:**
- Use `${data-testid}` if available (inspect Bing page — may not exist)
- Use text-based selectors: `page.get_by_text("Search")`
- Use role-based: `page.get_by_role("button", name="Search")`
- Always `await page.wait_for_load_state("domcontentloaded")` after navigation
- For search input: `await page.wait_for_selector("input[name='q']", state="visible")`
- Set reasonable default timeout: `page.set_default_timeout(10000)` (10s)

**Warning signs:** `TimeoutError: waiting for selector ...` — indicates either selector wrong or page too slow. Adjust timeout but verify actual page load.

### Pitfall 3: Implicit Time-Based Assertions

**What goes wrong:** Using `time.sleep(3)` to "wait for page" or asserting that something happened "within X seconds" by checking `time.time()`.

**Why it happens:** Developer wants to synchronize but uses clock instead of element state.

**How to avoid:**
- Replace sleeps with explicit waits: `await page.wait_for_selector(".some-class", state="attached")`
- If measuring performance, record timestamps but don't base test pass/fail on elapsed time (except for overall suite duration)
- Performance recording is informational; assertions should be about behavior, not speed.

**Warning signs:** Any `import time` followed by `time.sleep()` in test files.

### Pitfall 4: Environment Detection Skipping Entire Suite Silently

**What goes wrong:** All tests skipped with generic "environment not available" message, confusing developer.

**Why it happens:** Skipping at module import time or using broad conditions.

**How to avoid:**
- Perform environment detection in `conftest.py` session-scoped fixture that runs once
- Print clear skip message with actionable instructions: "Run: playwright install chromium"
- If only one test depends on environment, skip that test individually
- Use `pytest.skip(reason)` not `sys.exit()` or raising exceptions

**Warning signs:** `collected 0 items` or all `s SKIPPED` with no clear reason.

### Pitfall 5: State Leakage Between Tests Despite Context Isolation

**What goes wrong:** One test sets localStorage or cookies that affect subsequent tests.

**Why it happens:** Not actually using fresh context; reusing context inadvertently; or using session storage in browser that persists across contexts.

**How to avoid:**
- Ensure `context` fixture is function-scoped and always creates new context: `await browser.new_context()`
- Never set global state in fixtures with broader scope (session/package)
- If test needs clean slate, explicitly call `await context.clear_cookies()` and `await context.clear_storage()` before actions
- Verify by logging storage size pre/post test during development

**Warning signs:** Tests pass individually but fail when run as a suite.

### Pitfall 6: Internet Dependency Causing CI Flakiness

**What goes wrong:** Smoke tests fail on CI because Bing is unreachable or slow (network issues, rate limiting).

**Why it happens:** Smoke tests require internet access to reach bing.com; CI network may be throttled or blocked.

**How to avoid:**
- Keep smoke tests minimal and fast to reduce exposure window
- Set aggressive but reasonable timeouts: navigation timeout 15s, overall test timeout 30s
- If CI consistently cannot reach Bing, consider graceful skip (but that defeats purpose of smoke) — instead fix CI network egress
- Do not mock; smoke must validate real browser access
- Use Bing's public domain `www.bing.com` (not rewards subdomain) to avoid geo-restrictions

**Warning signs:** `TimeoutError` navigating to `https://www.bing.com` on CI but not local. Check CI network policies.

## Code Examples

Verified patterns from Project's Phase 1 implementation and Playwright best practices:

### Environment Check and Skip

```python
# Source: tests/e2e/helpers/environment.py
def is_ci_environment() -> bool:
    """Check if running in CI environment."""
    return any(
        os.environ.get(var)
        for var in ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "CIRCLECI", "JENKINS_URL"]
    )

# In smoke test:
def test_browser_launch(page: Page):
    import pytest
    from tests.e2e.helpers.environment import is_ci_environment

    # This test runs in any environment; browser fixture ensures launch
    assert page is not None
```

### Failure Capture Hook

```python
# Source: tests/e2e/conftest.py (pytest hook)
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        item._e2e_failed = True

@pytest.fixture(autouse=True)
async def _capture_failure_on_error(request: Any, page: Page):
    yield
    if hasattr(request.node, "_e2e_failed") and request.node._e2e_failed:
        from tests.e2e.helpers.screenshot import capture_failure_screenshot
        artifacts = await capture_failure_screenshot(page, request.node.name, request)
        logging.error(f"Test failed. Artifacts saved: {artifacts}")
```

### Basic Search Test Pattern (No Login)

```python
# tests/e2e/smoke/test_search_flow.py
import pytest
from playwright.async_api import Page, expect

@pytest.mark.smoke
@pytest.mark.no_login
async def test_basic_search_execution(page: Page):
    """Execute a single search and verify results page loads."""
    # Navigate to Bing
    await page.goto("https://www.bing.com", wait_until="domcontentloaded")

    # Accept cookies if banner present (optional)
    try:
        accept_btn = page.get_by_role("button", name="Accept")
        await accept_btn.click(timeout=3000)
    except:
        pass  # No banner, continue

    # Fill search input
    search_input = page.locator("input[name='q']")
    await search_input.fill("playwright python")
    await search_input.press("Enter")

    # Verify results page
    await page.wait_for_load_state("domcontentloaded")
    results_header = page.get_by_text("Results")
    await expect(results_header).to_be_visible(timeout=10000)

    # Verify page title contains search term
    assert "playwright" in page.title().lower()
```

### Performance Timing and Summary

```python
# tests/e2e/smoke/conftest.py (partial)
import time
import json
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def smoke_profiler():
    """Track test durations and print summary."""
    profiler = {"start": time.perf_counter(), "tests": []}
    yield profiler
    total = time.perf_counter() - profiler["start"]
    print(f"\n{'='*60}")
    print(f"SMOKE SUITE SUMMARY")
    print(f"{'='*60}")
    for t in profiler["tests"]:
        print(f"  {t['name']}: {t['duration']:.3f}s")
    print(f"{'='*60}")
    print(f"Total: {total:.3f}s")
    if total > (45 if is_ci_environment() else 30):
        print(f"WARNING: Suite exceeded threshold! ({total:.3f}s)")
    print(f"{'='*60}\n")

    # Write profile to file
    profile_path = Path("logs/e2e/smoke/profile.json")
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(json.dumps({
        "total_seconds": total,
        "passed": total <= (45 if is_ci_environment() else 30),
        "tests": profiler["tests"],
    }, indent=2))

@pytest.fixture
def track_duration(request, smoke_profiler):
    """Record duration of each test."""
    start = time.perf_counter()
    yield
    duration = time.perf_counter() - start
    smoke_profiler["tests"].append({
        "name": request.node.name,
        "duration": duration,
    })
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual sleep-based waits | Explicit wait_for_load_state and expect assertions | Playwright v1.0+ | More reliable, less flaky |
| Global browser context | Function-scoped context per test | Modern pytest | Better isolation, no state leakage |
| Implicit timeouts | Configurable default timeout + per-action timeout | Best practices 2023 | Faster failure, easier debugging |
| No environment skipping | Two-stage detection (static + browser) | Phase 1 decisions | Clearer skip reasons, better DX |
| Inline screenshots | pytest hook with in-test capture | Phase 1 decisions | Simpler, no race conditions |
| Synchronous tests | Async/await pattern | Playwright Python 1.0+ | Required for modern Playwright |

**Deprecated/outdated:**
- **`page.expect_navigation()`** for simple waits — too heavyweight; prefer `wait_for_load_state`
- **`browser.new_page()` in tests** without fixture cleanup — leads to orphan pages; always use fixtures
- **`time.sleep()`** for synchronization — causes unnecessary delays; use element waits
- **Global pytest fixtures with broad scope** (e.g., module-scoped context) — causes state leakage; keep function-scoped

## Open Questions

1. **What specific Bing selectors are stable?**
   - What we know: Bing uses standard input[name='q'] for search box
   - What's unclear: Exact selector for search button or results container may vary by locale/theme
   - Recommendation: Implement tests with flexibility; use role-based selectors or fallback to text

2. **Should smoke tests include mobile viewport simulation?**
   - Decision D-04 excludes mobile from Phase 2 focus
   - Recommendation: Defer to Phase 4; smoke stays minimal (<30s)

3. **How to handle Bing UI changes breaking smoke tests?**
   - What we know: Bing occasionally updates DOM structure
   - What's unclear: How often and impact severity
   - Recommendation: Add BDD-style assertions using text content rather than deep DOM paths

4. **Flakiness tracking storage format**
   - What we know: Need to record pass/fail counts per test over last N runs
   - What's unclear: Where to store (single file vs per-run subdirectory), how to aggregate
   - Recommendation: Single JSON file `logs/e2e/flakiness.json` with append-only entries; compute stats at suite end

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3.10+ | Runtime | ✓ (assuming project uses 3.10+) | 3.10+ | N/A |
| pytest | Test framework | ✓ (in dev deps) | >=8.0.0 | N/A |
| pytest-asyncio | Async tests | ✓ (in dev deps) | >=0.24.0 | N/A |
| playwright | Browser automation | ✓ (in dev deps) | >=1.49.0 | N/A |
| Chromium browser | Actual browser | ✗ (not yet installed) | — | Install via `playwright install chromium` |

**Missing dependencies with no fallback:**
- Chromium browser binary — must be installed via `playwright install chromium` before tests run

**Missing dependencies with fallback:**
- None. All are required.

**Note:** Phase 2 assumes Playwright browsers are installed. If not, two-stage detection will skip suite with clear instruction.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.x + pytest-asyncio 0.24.x |
| Config file | `pyproject.toml` (tool.pytest.ini_options) — smoke markers already defined |
| Quick run command | `pytest tests/e2e/smoke/ -v -m smoke` |
| Full suite command | `pytest tests/e2e/ -v` (includes smoke) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| E2E-002-01 | Browser launch and basic navigation (Bing homepage) | smoke | `pytest tests/e2e/smoke/test_environment.py::test_browser_launch -v` | ❌ Phase 2 |
| E2E-002-02 | Verify Bing search page loads and accepts input | smoke | `pytest tests/e2e/smoke/test_bing_health.py::test_search_input_visible -v` | ❌ Phase 2 |
| E2E-002-03 | Execute basic search and verify results page (<10s) | smoke | `pytest tests/e2e/smoke/test_search_flow.py::test_basic_search_execution -v` | ❌ Phase 2 |
| E2E-002-04 | Total smoke suite execution time <30s local / <45s CI | smoke (gate) | `pytest tests/e2e/smoke/ -v --durations=0` | ❌ Phase 2 |
| E2E-002-05 | Smoke suite pass rate ≥95% (≤1 failure per 20 runs) | quality gate | `pytest tests/e2e/smoke/ -v` (iterated) | ❌ Phase 2 |

### Sampling Rate

- **Per task commit:** `pytest tests/e2e/smoke/ -v` (fast <30s)
- **Per wave merge:** Same command + flakiness review of last 5 runs
- **Phase gate:** Smoke suite must pass 5 consecutive runs with ≥95% success before advancing to Phase 3

### Wave 0 Gaps

- [ ] `tests/e2e/smoke/conftest.py` — smoke-specific fixtures (performance profiling, flakiness tracking)
- [ ] `tests/e2e/smoke/helpers/performance.py` — profiling utilities
- [ ] `tests/e2e/smoke/helpers/flakiness.py` — flakiness storage and reporting
- [ ] `tests/e2e/smoke/test_environment.py` — browser launch + navigation test
- [ ] `tests/e2e/smoke/test_bing_health.py` — search input visibility test
- [ ] `tests/e2e/smoke/test_search_flow.py` — basic search execution
- [ ] `tests/e2e/smoke/test_summary.py` — final suite summary hook
- [ ] Extend `tests/e2e/helpers/environment.py` with two-stage pre-check functions

## Sources

### Primary (HIGH confidence)

- `tests/e2e/conftest.py` (Phase 1) — Existing patterns for fixtures, failure capture, environment detection
- `tests/e2e/helpers/environment.py` (Phase 1) — CI detection utilities
- `pyproject.toml` — pytest configuration, markers, timeout settings
- `.planning/phases/02-smoke-tests/02-CONTEXT.md` — Decisions D-01 through D-25 (authoritative scope and constraints)

### Secondary (MEDIUM confidence)

- [Playwright Python Documentation](https://playwright.dev/python/) — API reference for page actions, waits, timeouts
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/) — Async test patterns
- [Playwright Best Practices Guide](https://playwright.dev/docs/best-practices) — General recommendations (verified via official docs)

### Tertiary (LOW confidence)

- Web search results for "Playwright pytest best practices 2024" — General community patterns, not specific to this project

---

**Confidence breakdown:**
- Standard stack: HIGH — Project already has dependencies; based on Phase 1 implementation
- Architecture: HIGH — Clear continuation of Phase 1 patterns; decisions locked in CONTEXT.md
- Pitfalls: HIGH — Based on common E2E testing anti-patterns and project's own guidelines
- Performance strategies: MEDIUM — Derived from general Playwright best practices; need to validate thresholds (30s/45s) in implementation