"""Smoke tests for search functionality."""

import pytest
from playwright.async_api import Page, expect

pytestmark = [pytest.mark.smoke, pytest.mark.no_login]


class TestSearchExecution:
    """Verify search works end-to-end without login."""

    async def test_basic_search_returns_results(self, page: Page, track_smoke_duration):
        """
        Execute a single search and verify results page loads.
        This is the core smoke test for Bing search functionality.
        """
        await page.goto("https://www.bing.com", wait_until="domcontentloaded", timeout=30000)

        # Handle cookie banner if present (EU users)
        try:
            accept_btn = page.get_by_role("button", name="Accept", exact=True).first
            await accept_btn.click(timeout=2000)
        except Exception:
            pass  # No banner, continue

        # Perform search
        search_input = page.locator("input[name='q']")
        await expect(search_input).to_be_visible(timeout=20000)
        await search_input.fill("playwright python automation")
        await search_input.press("Enter")

        # Verify results page
        await page.wait_for_load_state("domcontentloaded", timeout=30000)

        # Check for results container (Bing's standard)
        results = page.locator(".b_algo")
        count = await results.count()
        assert count > 0, "No search results found"

        # Sanity: page title contains search term
        title = await page.title()
        assert "playwright" in title.lower() or "automation" in title.lower()

    async def test_multiple_searches_stable(self, page: Page, track_smoke_duration):
        """
        Execute 3 consecutive searches to verify stability.
        Each search should complete within 10s.
        """
        queries = ["python testing", "playwright docs", "async await python"]

        for query in queries:
            await page.goto("https://www.bing.com", wait_until="domcontentloaded", timeout=30000)

            search_input = page.locator("input[name='q']")
            await expect(search_input).to_be_visible(timeout=20000)
            await search_input.fill(query)
            await search_input.press("Enter")

            await page.wait_for_load_state("domcontentloaded", timeout=30000)
            results = page.locator(".b_algo")
            count = await results.count()
            assert count > 0, f"No results for query: {query}"
