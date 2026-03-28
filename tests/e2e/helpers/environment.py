"""Environment detection utilities for E2E tests."""

import os


def is_ci_environment() -> bool:
    """Check if running in CI environment."""
    return any(
        os.environ.get(var)
        for var in ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "CIRCLECI", "JENKINS_URL"]
    )


def is_local_development() -> bool:
    """Check if running in local development environment."""
    return not is_ci_environment()


def get_environment_type() -> str:
    """Get current environment type."""
    if is_ci_environment():
        return "ci"
    elif is_local_development():
        return "local"
    else:
        return "unknown"


def check_playwright_installed() -> tuple[bool, str]:
    """
    Stage 1: Static check for Playwright driver and browsers.
    Fast, doesn't launch browser.
    """
    try:
        from playwright._impl._driver import compute_driver_executable

        compute_driver_executable()
        return True, ""
    except Exception as e:
        return False, f"Playwright drivers not found: {e}"


def check_browser_binary() -> tuple[bool, str]:
    """
    Stage 2: Dynamic check - try launching Chromium headless.
    More expensive but validates actual browser availability.
    """
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
    """
    Validate smoke test environment.
    Skip entire suite with actionable message if dependencies missing.
    """
    import pytest

    ok, msg = check_playwright_installed()
    if not ok:
        pytest.skip(
            f"[SKIP] Playwright not installed. Run: playwright install chromium. Details: {msg}"
        )

    # Note: browser binary check moved to test_browser_launches to avoid asyncio.run() conflict
    # Each test that needs browser will handle timeout gracefully
