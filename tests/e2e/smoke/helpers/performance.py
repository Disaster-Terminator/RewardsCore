import json
import time
from pathlib import Path

from tests.e2e.helpers.environment import is_ci_environment
from tests.e2e.smoke.helpers.flakiness import get_flakiness_report

def print_smoke_summary(profiler: dict, total: float):
    """Print summary and include flakiness warnings."""
    ci = is_ci_environment()
    threshold = 45 if ci else 30

    print(f"\n{'=' * 60}")
    print(f"SMOKE SUITE SUMMARY (CI: {ci}, Session: {profiler['session_id']})")
    print(f"{'=' * 60}")
    for t in profiler["tests"]:
        status = "✓" if t.get("passed", True) else "✗"
        print(f"  {status} {t['name']}: {t['duration']:.3f}s")
    print(f"{'=' * 60}")
    print(f"Total: {total:.3f}s (threshold: {threshold}s)")
    if total > threshold:
        print("⚠️  WARNING: Suite exceeded performance threshold!")
    print(f"{'=' * 60}")

    # Flakiness report
    report = get_flakiness_report(window=5)
    flaky_tests = [name for name, data in report.items() if data["flaky"]]
    if flaky_tests:
        print("\n" + "!" * 60)
        print("FLAKINESS ALERT: The following tests are unstable:")
        for name in flaky_tests:
            data = report[name]
            print(
                f"  - {name}: {data['pass_rate'] * 100:.1f}% pass rate ({data['passed']}/{data['total_runs']})"
            )
        print("!" * 60)
        print("Consider quarantining or redesigning these tests.\n")

    # Save profile
    profile_dir = Path("logs") / "e2e" / "smoke"
    profile_dir.mkdir(parents=True, exist_ok=True)
    profile_path = profile_dir / "profile.json"
    profile = {
        "total_seconds": total,
        "passed": total <= threshold,
        "threshold": threshold,
        "ci": ci,
        "tests": profiler["tests"],
        "session_id": profiler["session_id"],
        "flakiness_report": report,
    }
    profile_path.write_text(json.dumps(profile, indent=2))
