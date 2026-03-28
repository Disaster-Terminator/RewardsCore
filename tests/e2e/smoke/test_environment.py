"""Smoke environment validation tests."""

import pytest

from tests.e2e.helpers.environment import require_smoke_environment

pytestmark = [pytest.mark.smoke]


def test_smoke_environment_readiness():
    """
    Verify all smoke test prerequisites are met.
    This test runs first and provides clear skip reasons if environment not ready.
    """
    require_smoke_environment()
    assert True  # If we reach here, checks passed


@pytest.mark.asyncio
async def test_browser_launches(browser):
    """
    Verify Playwright Chromium browser launches successfully.
    Uses session-scoped browser from Phase 1 fixtures.
    """
    assert browser is not None
    assert browser.is_connected()


@pytest.mark.asyncio
async def test_browser_context_creation(browser):
    """Verify we can create isolated browser contexts."""
    context = await browser.new_context()
    assert context is not None
    await context.close()
