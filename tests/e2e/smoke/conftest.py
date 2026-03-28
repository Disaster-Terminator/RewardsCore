"""Smoke test suite configuration: profiling, flakiness tracking, and summary."""

import json
import time
from pathlib import Path

import pytest

from tests.e2e.helpers.environment import is_ci_environment
from tests.e2e.smoke.helpers.flakiness import record_outcome
from tests.e2e.smoke.helpers.performance import print_smoke_summary


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test outcomes for flakiness tracking and pass/fail status."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        test_name = item.nodeid
        passed = report.passed
        duration = getattr(item, "_smoke_duration", 0)
        session_id = (
            item._request.config.stash.get("smoke_session_id", 0)
            if hasattr(item, "_request")
            else 0
        )
        record_outcome(test_name, passed, duration, session_id)
        # Store passed status for use in track_smoke_duration
        item._smoke_passed = passed


def pytest_configure(config):
    """Assign a unique session ID for this pytest run."""
    config.stash["smoke_session_id"] = int(time.time())


@pytest.fixture(scope="session", autouse=True)
def smoke_profiler(request) -> dict:
    """Session-scoped profiler that also exposes session_id to hooks."""
    profiler = {"start": time.perf_counter(), "tests": [], "session_id": int(time.time())}
    # Make session_id available to pytest hook
    request.config.stash["smoke_session_id"] = profiler["session_id"]
    yield profiler
    total = time.perf_counter() - profiler["start"]
    print_smoke_summary(profiler, total)




@pytest.fixture
def track_smoke_duration(request, smoke_profiler):
    """Record execution time and expose to flakiness hook."""
    start = time.perf_counter()
    yield
    duration = time.perf_counter() - start
    smoke_profiler["tests"].append(
        {
            "name": request.node.name,
            "duration": duration,
            "passed": getattr(request.node, "_smoke_passed", True),  # set by pytest hook
        }
    )
    request.node._smoke_duration = duration
