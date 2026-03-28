"""Performance and determinism gates for smoke suite."""

import json
from pathlib import Path

import pytest


@pytest.mark.smoke
def test_smoke_suite_performance():
    """Verify total smoke suite time is within threshold."""
    profile_path = Path("logs/e2e/smoke/profile.json")
    if not profile_path.exists():
        pytest.skip("No profile found (suite may not have run)")

    profile = json.loads(profile_path.read_text())
    threshold = 45 if profile.get("ci") else 30
    actual = profile["total_seconds"]
    assert actual <= threshold, f"Smoke suite took {actual:.2f}s, exceeds {threshold}s threshold"


@pytest.mark.smoke
def test_smoke_suite_passed():
    """Verify smoke suite reported success (no threshold failures)."""
    profile_path = Path("logs/e2e/smoke/profile.json")
    if not profile_path.exists():
        pytest.skip("No profile found")

    profile = json.loads(profile_path.read_text())
    assert profile["passed"], "Smoke suite performance gate failed"


@pytest.mark.smoke
def test_flakiness_data_exists():
    """Verify flakiness tracking database exists and has entries."""
    flakiness_path = Path("logs/e2e/flakiness.jsonl")
    assert flakiness_path.exists(), "Flakiness database not created"
    # Check that we have at least some entries after running tests
    lines = flakiness_path.read_text().strip().split("\n") if flakiness_path.exists() else []
    assert len(lines) > 0, "No flakiness data recorded"
