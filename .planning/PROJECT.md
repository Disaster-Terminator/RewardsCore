# RewardsCore E2E & Smoke Test Suite

**Project:** E2E Testing Framework for RewardsCore
**Type:** Quality Assurance Initiative
**Created:** 2026-03-21
**Branch:** feature/e2e-testing
**Milestone:** M1 - Smoke Tests Ready

---

## What This Is

This project adds a comprehensive end-to-end (E2E) and smoke test suite to RewardsCore, ensuring that core functionalities (login, search, tasks) remain stable and reliable across changes.

The test suite uses **Playwright** for real browser automation and is designed with **decoupled modules** so that login tests and search tests can run independently.

---

## Core Value

**Independent verification** of critical user journeys without requiring full application context or manual setup. Tests must be:
- Fast (smoke < 30s, E2E < 5min per scenario)
- Reliable (≥90% pass rate, minimal flakiness)
- Self-diagnosing (auto-capture screenshots/logs on failure)
- Environment-friendly (support both real accounts and mock scenarios)

---

## Requirements

### Validated

- [x] **E2E-001**: Test Infrastructure Setup
- [x] **E2E-008**: Test Data Management
- [x] **E2E-002**: Smoke Test Suite Implementation

### Active
- [ ] **E2E-003**: Login E2E Tests
- [ ] **E2E-004**: Search E2E Tests (No-Login Mode)
- [ ] **E2E-005**: Search E2E Tests (With-Login Mode)
- [ ] **E2E-006**: Task E2E Tests
- [ ] **E2E-007**: CI/CD Integration
- [ ] **E2E-008**: Test Data Management

### Out of Scope

- [ ] Unit tests — Already covered in `tests/unit/`
- [ ] Performance/load testing — Separate effort
- [ ] Mobile browser testing — Desktop only
- [ ] Third-party API mocking — Use existing fixtures
- [ ] Cross-browser testing — Chromium only

---

## Context

**Existing Test Coverage:**
- Unit tests: ~316 tests in `tests/unit/`
- Integration tests: 1 file (`test_query_engine_integration.py`)
- Manual test checklist: `tests/manual/login_test_checklist.md`

**Gaps Identified:**
- ❌ No E2E tests for complete workflows
- ❌ No smoke tests for quick validation
- ❌ No decoupled login/search testing
- ❌ No CI/CD automated browser testing

**Technical Debt Note:**
The current codebase has a separate `.planning-technical-debt/` project for code simplification. This E2E testing project runs in parallel and does not interfere with that effort.

---

## Constraints

- **Browser**: Playwright with Chromium (same as main code)
- **Isolation**: Each test gets fresh browser context, 100% cleanup
- **Headless**: Supported for CI, optional for local dev
- **Accounts**: Use dedicated test Microsoft accounts, credentials via CI secrets
- **Runtime**: Smoke < 30s total, E2E < 5min per scenario
- **Flakiness**: Target < 5% retry rate

---

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use pytest-asyncio | Consistent with existing test stack | Pending |
| Separate smoke/e2e directories | Fast feedback vs comprehensive validation | Pending |
| No-login-first for search tests | Reduce account lock risk, improve stability | Pending |
| Per-test browser context | Ensure isolation, no state leakage | Pending |

---

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

*Last updated: 2026-03-21 after initialization*
