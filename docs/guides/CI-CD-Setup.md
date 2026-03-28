# CI/CD Setup for E2E Tests

## GitHub Actions Integration

### Workflows

1. **Smoke Tests** (`.github/workflows/e2e-smoke.yml`)
   - Triggers: Push to main/develop, PRs
   - Scope: Smoke tests only (no-login + basic validation)
   - Duration: <15 min
   - Purpose: Fast feedback for every change

2. **Full E2E Tests** (`.github/workflows/e2e-full.yml`)
   - Triggers: Daily at 6 PM UTC, manual dispatch
   - Scope: Full E2E suite (login, search, tasks)
   - Duration: <30 min
   - Purpose: Comprehensive validation, points tracking

### Required Secrets

See `.github/SECRETS.md` for detailed setup.

### Artifacts

Each workflow uploads:
- Test results (JUnit XML)
- Screenshots on failure
- Logs (`logs/e2e/`)
- Diagnostic reports
- Storage state (smoke workflow)

### Flakiness Detection

Current: Manual review of CI runs

Future: Implement `pytest-rerunfailures` with `--count=3` and flag tests with >1 failure.

### Performance Benchmarks

Workflows include performance checks:
- Smoke suite total <30s (measured locally, CI may be slower)
- Search page load <3s, search execution <5s (from `test_search_performance.py`)

### Notifications

Currently: Repository maintainers review Actions tab

Optional: Add Slack/Discord webhook on failure:
```yaml
- uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    channel: '#e2e-tests'
  if: always()
```

### Maintenance

- Monthly: Review CI duration, optimize slow tests
- Quarterly: Update Playwright dependencies, test against Bing UI changes
