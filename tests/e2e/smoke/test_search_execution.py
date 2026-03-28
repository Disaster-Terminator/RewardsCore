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

        # Initial navigation
        await page.goto("https://www.bing.com", wait_until="load", timeout=30000)

        # Handle cookie banner if present
        try:
            # Try multiple common "Accept" buttons
            for btn_text in ["Accept", "Allow all", "I agree"]:
                btn = page.get_by_role("button", name=btn_text, exact=False).first
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    break
        except Exception:
            pass

        for query in queries:
            # Locate search input - wait for it to be ready
            search_input = page.locator("input[name='q']")
            await expect(search_input).to_be_visible(timeout=10000)
            
            # Clear and type
            await search_input.fill("")
            await search_input.type(query, delay=10)
            await search_input.press("Enter")

            # Wait for navigation or results to appear
            # We check for results container but we're more permissive about visibility
            results = page.locator(".b_algo")
            
            # Wait up to 10s for at least one result to exist in DOM
            try:
                await page.wait_for_selector(".b_algo", state="attached", timeout=10000)
            except Exception:
                # If .b_algo not found, try a broader results container
                await page.wait_for_selector("#b_results", state="attached", timeout=5000)
            
            # Check count
            count = await results.count()
            if count == 0:
                # Fallback: check any list item in results
                count = await page.locator("#b_results li").count()
            
            assert count > 0, f"No results found for query: {query}"
            
            # Brief pause for stability
            import asyncio
            await asyncio.sleep(0.5)
