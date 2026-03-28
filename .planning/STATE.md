---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 02
status: unknown
last_updated: "2026-03-23T17:19:26.032Z"
progress:
  total_phases: 6
  completed_phases: 2
  total_plans: 15
  completed_plans: 5
---

# STATE

**Project:** RewardsCore E2E & Smoke Test Suite
**Milestone:** M1 - Smoke Tests Ready
**Current Phase:** 02
**Branch:** feature/e2e-testing
**Last Updated:** 2026-03-22

---

## Project Reference

**Core Value:**
Independent verification of critical user journeys without requiring full application context or manual setup. Tests must be fast (<30s smoke, <5min E2E), reliable (≥90% pass), self-diagnosing, and environment-friendly.

**Current Focus:**
Phase 02 — smoke-tests

**Constraints:**

- Browser: Playwright Chromium only
- Isolation: Per-test fresh context with 100% cleanup
- Accounts: CI secrets, dedicated test accounts
- Runtime: Smoke <30s, E2E <5min, flakiness <5%

---

## Current Position

Phase: 02 (smoke-tests) — EXECUTING
Plan: 1 of 2

## Performance Metrics

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Test framework setup time | < 2 hours | - | - |
| Fixture reliability (pass rate) | 100% | - | - |
| Test context cleanup | 100% | - | - |
| Screenshot on failure | Enabled | - | - |

*Metrics will be populated during execution.*

---

## Accumulated Context

### Key Decisions (so far)

| Decision | Rationale | Status |
|----------|-----------|--------|
| Use pytest-asyncio | Consistent with existing test stack | Decided |
| Separate smoke/e2e directories | Fast feedback vs comprehensive validation | Decided |
| No-login-first for search tests | Reduce account lock risk, improve stability | Decided |
| Per-test browser context | Ensure isolation, no state leakage | Decided |
| Chromium only | Align with main app, reduce complexity | Decided |
| Real browser tests (no mocking) | Validate actual user experience | Decided |
| Phase 2: No-credentialed smoke | Fast, stable, no external dependencies | Decided |
| Phase 2: Performance thresholds (<30s local, <45s CI) | Balance feedback speed with CI reality | Decided |
| Phase 2: Flakiness monitoring (not blocking) | Record and warn, don't block PRs | Decided |
| Phase 2: Two-stage environment detection | Clear skip reasons, better DX | Decided |

### Open Questions

- Which test accounts to use for CI vs local development? (needs 2 dedicated Microsoft accounts)
- Should tests run with `--headed` locally for debugging? (likely yes, but CI headless)
- How to handle Bing UI changes breaking selectors? (monitoring + alerting)
- Task test data: auto-discover or predefine scenarios? (hybrid approach)

### Known Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Bing UI changes | Medium | High | Robust selectors + screenshots + weekly health check |
| Account lockout | Low | High | Dedicated test account, staggered runs |
| Network flakiness | Medium | Medium | Timeouts + retry (≤1) + verbose logs |
| CI secrets errors | Medium | High | Local validation script + docs |
| Playwright drift | Low | Medium | Pin versions, CI cache |

### Dependencies & Blockers

**External:**

- Need 2 dedicated Microsoft Rewards test accounts (email + password + optional 2FA)
- CI secrets setup: `MS_REWARDS_E2E_EMAIL`, `MS_REWARDS_E2E_PASSWORD`, `MS_REWARDS_E2E_TOTP_SECRET`
- GitHub repository with Actions enabled

**Internal:**

- None yet

---

## Session Continuity

### What Just Happened

- Phase 1 (基础设施与数据设置) COMPLETED ✅
- All deliverables for 01-01, 01-02, 01-03 implemented successfully:
  ✓ Directory structure: tests/e2e/{data,fixtures,helpers,login,search,smoke,tasks}
  ✓ Data files: search_terms.txt, accounts.yaml, scenarios.py, mobile_viewports.yaml
  ✓ Helpers: account_health.py, decorators.py, environment.py, screenshot.py
  ✓ Fixtures: storage_state.json placeholder
  ✓ Templates: .env.test.example
  ✓ .gitignore updated with E2E exclusions

- All Python imports verified working
- Phase 1 requirements E2E-001 and E2E-008 marked complete

### Next Actions (for human or next agent)

1. **Start Phase 2 execution** — Run `/gsd:execute-phase 2` to implement smoke test suite
2. **Set up test accounts** — Acquire credentials before Phase 3/4/5 implementation
3. **Configure CI secrets** — Prepare GitHub Actions secrets template
4. **Monitor Phase 2 progress** — Smoke tests must achieve ≥95% pass rate

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260322-jsl | 配置 pre-commit，集成 ruff、ruff-format 和 mypy | 2026-03-22 | 074d666 | [260322-jsl-discuss-conda](./quick/260322-jsl-discuss-conda/) |
| 01-02 | Browser fixtures with failure capture | 2026-03-22 | 3cdfd3e | [01-02](./phases/01-基础设施与数据设置/01-02-SUMMARY.md) |
| 01-03 | Test data management (full implementation) | 2026-03-23 | - | [01-03](./phases/01-基础设施与数据设置/01-03-SUMMARY.md) |

---

*State last written: 2026-03-22 — Quick task 260322-jsl completed (pre-commit config updated)*

- Phase 1 combines E2E-001 (Infrastructure) and E2E-008 (Test Data)
- Granularity: standard (5–8 expected, we have 6)
- Goal-backward thinking applied: success criteria are observable user/test behaviors
- No orphaned requirements
- Deliverables: 15 plans total across 6 phases (3+2+3+3+2+2)
- Phase 2 is a milestone gate: smoke tests must pass before other test suites developed
- Payload consistency: PUT /api/v1/rewards { "amount": 500 } — fix consistency</hash>

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| E2E-001 | Phase 1 | ✅ Completed |
| E2E-008 | Phase 1 | ✅ Completed |
| E2E-002 | Phase 2 | Pending |
| E2E-003 | Phase 3 | Pending |
| E2E-004 | Phase 4 | Pending |
| E2E-005 | Phase 4 | Pending |
| E2E-006 | Phase 5 | Pending |
| E2E-007 | Phase 6 | Pending |

**Coverage:** 8/8 (100%) ✓

---

*State last written: 2026-03-22 — Quick task 260322-jsl completed (pre-commit config updated)*
