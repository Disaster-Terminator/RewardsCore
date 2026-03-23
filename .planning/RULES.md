# GSD Agent Execution Rules

## E2E Test Execution Standards

All test commands in phase plans MUST follow these rules:

### 1. Always Use Parallel Execution

All pytest commands MUST include `-n auto` or explicit `-n <cores>`:

```bash
# ✓ Correct
pytest -n auto tests/e2e/smoke/ -v
pytest -n 4 tests/e2e/login/ -v  # explicit cores also fine

# ✗ Wrong (no parallel)
pytest tests/e2e/smoke/ -v
```

**Rationale:** E2E tests are I/O-bound (network, browser waits). Parallel execution provides 2-4x speedup locally and in CI.

### 2. Conda Environment Activation

Agent should execute tests using ONE of these methods (in precedence order):

**Option A: Direct python path using CONDA_PREFIX (preferred, fastest)**
```bash
${CONDA_PREFIX}/bin/python -m pytest -n auto tests/e2e/smoke/ -v
```
This works if CONDA_PREFIX is set (conda activate is in effect).

**Option A Fallback: Absolute path**
```bash
/home/raystorm/miniconda3/envs/rewards-core/bin/python -m pytest -n auto tests/e2e/smoke/ -v
```
Use this when CONDA_PREFIX is not set but we know the expected path.

**Option B: conda run (reliable but slightly slower due to extra process spawn)**
```bash
conda run -n rewards-core python -m pytest -n auto tests/e2e/smoke/ -v
```
Use this when we cannot guarantee CONDA_PREFIX is set and want conda to handle environment resolution.

**Never:**
- `conda activate` followed by `pytest` (activation is shell-persistent; Agent commands run in ephemeral shells)
- Plain `pytest` without ensuring correct conda environment
- `python -m pytest` without absolute path or conda wrapper

### 3. Working Directory

- Always run pytest from repository root
- Use relative paths for test locations: `tests/e2e/smoke/`, `tests/e2e/login/`, etc.
- Do not `cd` into test directories; keep consistent from root

### 4. Timeout and Fail-Fast

For validation runs (e.g., smoke tests):
```bash
pytest -n auto --timeout=120 -x tests/e2e/smoke/ -v
```
- `--timeout=120` prevents hung tests
- `-x` stops on first failure during "smoke" validation

For full runs:
```bash
pytest -n auto --timeout=300 tests/e2e/ -v
```
Allow longer timeouts for complex scenarios (login with 2FA, task execution).

### 5. Artifact Collection

Always ensure test artifacts are captured on failure:

```bash
# These should already be configured in conftest.py (Phase 1)
# - Screenshots: logs/e2e/screenshots/{test_name}_{timestamp}.png
# - Console logs: logs/e2e/console_logs/
# - Diagnostic reports: logs/diagnosis/ (if --diagnose enabled)
```

If a test fails, Agent should:
1. Check `logs/e2e/screenshots/` for latest failure screenshot
2. Include artifact paths in SUMMARY.md
3. Do NOT attempt to clean up artifacts (leave for human review)

### 6. Markers and Filtering

Use pytest markers to target specific test subsets:

```bash
# Run only smoke tests
pytest -n auto -m "smoke" tests/e2e/ -v

# Run only tests requiring login
pytest -n auto -m "requires_login" tests/e2e/ -v

# Run only no-login tests (default for search)
pytest -n auto -m "no_login" tests/e2e/ -v

# Exclude slow tests
pytest -n auto -m "not slow" tests/e2e/ -v
```

### 7. Environment Variables

Phase plans may specify required environment variables. Agent must ensure they are set before execution:

```bash
# Example for tests needing credentials
export MS_REWARDS_E2E_EMAIL="test@outlook.com"
export MS_REWARDS_E2E_PASSWORD="secret"
# Then run pytest
```

If credentials are missing, tests should skip (not fail). This is handled by test code (pytest.skip).

### 8. Preflight Checks

Before running any E2E test suite, Agent should optionally run preflight validation:

```bash
# Verify environment
${CONDA_PREFIX}/bin/python -m pytest tests/e2e/test_environment.py -v

# Check Playwright browsers installed
playwright install chromium --with-deps
```

If preflight fails, halt and report issue rather than running full suite.

### 9. CI vs Local Distinction

Agents should NOT differentiate between CI and local unless explicitly specified in plan:

- Same commands work in both environments
- Headless mode is controlled by pytest fixtures or environment variable `E2E_HEADLESS`
- CI may set `-n 2` instead of `-n auto` to avoid resource contention (specify in plan if needed)

### 10. Command Templates for Phase Plans

When writing phase plan files, use these templates:

**General test execution:**
```bash
${CONDA_PREFIX}/bin/python -m pytest -n auto <test_path> -v --tb=short
```

**With timeout:**
```bash
${CONDA_PREFIX}/bin/python -m pytest -n auto --timeout=180 <test_path> -v
```

**With markers:**
```bash
${CONDA_PREFIX}/bin/python -m pytest -n auto -m "smoke" <test_path> -v
```

**Fail-fast validation:**
```bash
${CONDA_PREFIX}/bin/python -m pytest -n auto -x --timeout=120 <test_path> -v
```

---

## Compliance

All phase plans under `.planning/phases/` MUST follow these rules. If a plan specifies a command that violates these standards, Agent should:
1. Flag the inconsistency before execution
2. Use the correct command form as per this RULES.md
3. Note the deviation in the SUMMARY.md

---

*Last Updated: 2026-03-22*
