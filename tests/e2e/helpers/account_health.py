"""Account health check utilities for E2E tests."""

import os
from typing import Any, Callable

import pytest
from playwright.async_api import Page


async def check_account_health(page: Page) -> dict[str, Any]:
    """
    Check if the test account is healthy (not locked, has rewards access).

    Args:
        page: Playwright page with logged-in session

    Returns:
        Dict with 'healthy' (bool) and 'reason' (str) keys
    """
    try:
        # Navigate to rewards page to check account status
        await page.goto("https://rewards.bing.com/", timeout=10000)

        # Check for common account issues
        page_content = await page.content().lower()

        # Check for account locked message
        if "account" in page_content and "locked" in page_content:
            return {"healthy": False, "reason": "Account appears to be locked"}

        # Check for login redirect (not logged in)
        if "sign in" in page_content and "rewards" in page_content:
            return {"healthy": False, "reason": "Not logged in or session expired"}

        # Check for errors
        if "error" in page_content and "try again later" in page_content:
            return {"healthy": False, "reason": "Service error detected"}

        return {"healthy": True, "reason": "Account healthy"}

    except Exception as e:
        return {"healthy": False, "reason": f"Health check failed: {str(e)}"}


def requires_healthy_account(func: Callable) -> Callable:
    """
    Decorator to skip test if account is not healthy (D-20).

    Usage:
        @pytest.mark.asyncio
        @requires_healthy_account
        async def test_with_login(page):
            ...
    """
    async def wrapper(*args, **kwargs):
        # Extract page from args or kwargs
        page = None
        for arg in args:
            if hasattr(arg, "goto"):  # Playwright page
                page = arg
                break

        if page is None:
            pytest.skip("Cannot determine page for health check")

        health = await check_account_health(page)
        if not health["healthy"]:
            pytest.skip(f"Account not healthy: {health['reason']}")

        return await func(*args, **kwargs)

    return wrapper
