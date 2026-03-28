# Login E2E Tests - Framework

## Setup

1. Set environment variables:
   ```bash
   export MS_REWARDS_E2E_EMAIL=your_test@outlook.com
   export MS_REWARDS_E2E_PASSWORD=your_password
   export MS_REWARDS_E2E_TOTP_SECRET=  # Optional for 2FA accounts
   ```

2. Generate storage state (optional, speeds up tests):
   ```bash
   python scripts/save_storage_state.py
   # Uses headed mode, manually complete 2FA if needed
   ```

## Running Login Tests

```bash
# All login tests with parallel execution
pytest -n auto tests/e2e/login/ -v

# Specific test
pytest -n auto tests/e2e/login/test_login_flow.py::TestLoginFlow::test_successful_login -v

# With storage_state (faster)
export E2E_STORAGE_STATE=tests/fixtures/storage_state.json
pytest -n auto tests/e2e/login/ -v
```

## Health Checks

Tests use `account_health()` to skip if account locked or unavailable. Check `logs/e2e/` for health reports.
