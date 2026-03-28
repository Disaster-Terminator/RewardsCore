"""Track test outcomes across runs for flakiness analysis."""

import json
import time
from collections import defaultdict
from pathlib import Path

# JSONL storage — append-only, one entry per test execution
FLAKINESS_DB = Path("logs") / "e2e" / "flakiness.jsonl"


def record_outcome(test_name: str, passed: bool, duration: float, session_id: int):
    """Append test outcome to flakiness database."""
    entry = {
        "test": test_name,
        "passed": passed,
        "duration": duration,
        "session_id": session_id,
        "timestamp": time.time(),
    }
    FLAKINESS_DB.parent.mkdir(parents=True, exist_ok=True)
    with FLAKINESS_DB.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def get_flakiness_report(window: int = 5) -> dict:
    """
    Analyze last N **sessions** for each test and return flakiness metrics.
    Returns: {test_name: {pass_rate, total_runs, passed, flaky, sessions: []}}
    """
    if not FLAKINESS_DB.exists():
        return {}

    lines = FLAKINESS_DB.read_text().strip().split("\n")
    entries = [json.loads(line) for line in lines if line.strip()]

    # Group by test
    by_test = defaultdict(list)
    for entry in entries:
        by_test[entry["test"]].append(entry)

    report = {}
    for test, tests_entries in by_test.items():
        # Group by session to avoid counting parallel workers as separate "runs"
        by_session = defaultdict(list)
        for e in tests_entries:
            by_session[e["session_id"]].append(e)

        # Take most recent N sessions (ordered by max timestamp in session)
        sorted_sessions = sorted(
            by_session.values(), key=lambda sess: max(e["timestamp"] for e in sess), reverse=True
        )[:window]

        # Flatten to recent entries
        recent = [e for sess in sorted_sessions for e in sess]

        total = len(recent)
        passed = sum(1 for e in recent if e["passed"])
        pass_rate = passed / total if total > 0 else 1.0
        report[test] = {
            "pass_rate": round(pass_rate, 3),
            "total_runs": total,
            "passed": passed,
            "flaky": pass_rate < 0.95 and total >= 3,
            "sessions": [sess[0]["session_id"] for sess in sorted_sessions],  # for debugging
        }

    return report
