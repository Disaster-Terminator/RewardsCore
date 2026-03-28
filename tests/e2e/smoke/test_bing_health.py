"""Bing homepage health checks."""

import pytest
from playwright.async_api import Page, expect

pytestmark = [pytest.mark.smoke, pytest.mark.no_login]


class TestBingHealth:
    """Verify Bing is accessible and functional."""

    @pytest.mark.asyncio
    async def test_navigate_to_bing_homepage(self, page: Page, track_smoke_duration):
        """Navigate to Bing and verify homepage loads."""
        await page.goto(
            "https://www.bing.com",
            wait_until="domcontentloaded",
            timeout=30000,  # Increased from 15000 for WSL environments
        )
        title = await page.title()
        # Support both English and localized titles (e.g., Chinese: "搜索 - Microsoft 必应")
        assert "bing" in title.lower() or "microsoft" in title.lower(), f"Unexpected page title: {title}"

    @pytest.mark.asyncio
    async def test_search_input_present_and_interactable(self, page: Page, track_smoke_duration):
        """Verify search input is visible and can receive text."""
        await page.goto(
            "https://www.bing.com",
            wait_until="domcontentloaded",
            timeout=30000,  # Increased from 15000
        )

        # Use stable selector: input[name='q'] is Bing's standard search box
        search_input = page.locator("input[name='q']")
        await expect(search_input).to_be_visible(timeout=20000)  # Increased from 10000

        # Test interaction (fill + submit)
        await search_input.fill("playwright test")
        await page.keyboard.press("Enter")

        # Verify navigation to search results
        await page.wait_for_url(lambda url: "search?" in url, timeout=20000)  # Increased from 10000
