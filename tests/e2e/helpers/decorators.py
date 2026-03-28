"""Pytest decorators and guards for E2E tests."""

import os
from typing import Any, Callable

import pytest
from playwright.async_api import Page


def requires_e2e_credentials(func: Callable) -> Callable:
    """
    Decorator to skip test if E2E credentials are not available (D-20).

    Checks for MS_REWARDS_E2E_EMAIL and MS_REWARDS_E2E_PASSWORD env vars.

    Usage:
        @pytest.mark.asyncio
        @requires_e2e_credentials
        async def test_login_flow(page):
            ...
    """
    def wrapper(*args, **kwargs):
        email = os.environ.get("MS_REWARDS_E2E_EMAIL")
        password = os.environ.get("MS_REWARDS_E2E_PASSWORD")

        if not email or not password:
            pytest.skip(
                "E2E credentials not available. "
                "Set MS_REWARDS_E2E_EMAIL and MS_REWARDS_E2E_PASSWORD env vars. "
                "See .env.test.example for template."
            )

        return func(*args, **kwargs)

    return wrapper


async def prevent_prod_pollution(page: Page) -> None:
    """
    Guard to prevent production pollution in CI (D-22).

    Raises RuntimeError if running in CI environment and accessing
    production URLs.

    This is a safety measure to prevent accidental test runs against
    production from CI pipelines.

    Args:
        page: Playwright page to check

    Raises:
        RuntimeError: If in CI environment and accessing production URLs
    """
    from tests.e2e.helpers.environment import is_ci_environment

    if not is_ci_environment():
        return

    # Check current URL
    current_url = page.url.lower()

    # List of production URLs to protect
    prod_domains = [
        "rewards.microsoft.com",
        "www.bing.com/rewards",
    ]

    for domain in prod_domains:
        if domain in current_url:
            raise RuntimeError(
                f"SECURITY: CI environment detected accessing production domain: {domain}. "
                f"Current URL: {current_url}. "
                f"Tests should use test/staging environments or mock data in CI."
            )
