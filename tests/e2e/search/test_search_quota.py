import pytest
import re
from playwright.async_api import Page

class TestSearchQuota:
    """Tests that verify search quota tracking with authentication."""

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(120)
    async def test_search_increments_quota(self, search_with_points_check):
        """
        Performing searches should increment search quota/points on rewards dashboard.
        Note: Actual points per search vary; we verify that quota count increases.
        """
        page, get_points = search_with_points_check

        # Record initial quota from dashboard
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")
        initial_quota = await self._get_search_quota_from_dashboard(page)
        
        # Navigate to Bing homepage
        await page.goto("https://www.bing.com", wait_until="domcontentloaded")

        # Perform one search
        search_box = await page.wait_for_selector("input[name='q']", timeout=10000)
        await search_box.fill("test search quota increment")
        await page.keyboard.press("Enter")
        
        # Wait for results or some indicator
        try:
            await page.wait_for_selector(".b_algo", timeout=10000)
        except:
            # Fallback if specific result selector not found
            await page.wait_for_timeout(5000)

        # Navigate back to rewards dashboard
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")

        # Verify quota increased by at least 1
        new_quota = await self._get_search_quota_from_dashboard(page)
        assert new_quota > initial_quota, f"Search quota did not increase: {initial_quota} -> {new_quota}"

    async def _get_search_quota_from_dashboard(self, page: Page) -> int:
        """Extract search quota from rewards dashboard."""
        # Quota might be shown as "0/10" or "3/10" for daily searches
        # Try to find the search progress element
        try:
            # Common patterns for search quota
            selectors = [
                ".progressContainer",
                "[data-ct*='search']",
                ".points_status",
                "#searchPointsBreakdown"
            ]
            
            for selector in selectors:
                elements = await page.query_selector_all(selector)
                for el in elements:
                    text = await el.text_content()
                    if not text:
                        continue
                    # Match "X of Y" or "X / Y"
                    match = re.search(r'(\d+)\s*(?:of|/)\s*(\d+)', text)
                    if match:
                        return int(match.group(1))
            
            # If we can't find the X of Y pattern, try looking for just a number in a quota-like context
            # This is risky, but might work as fallback
        except Exception as e:
            print(f"DEBUG: Failed to extract quota: {e}")
            
        return 0

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(180)
    async def test_multiple_searches_increase_quota(self, search_with_points_check):
        """Multiple searches should accumulate until daily limit reached."""
        page, _ = search_with_points_check
        
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")
        initial_quota = await self._get_search_quota_from_dashboard(page)

        # Perform 3 searches
        for i in range(3):
            await page.goto("https://www.bing.com", wait_until="domcontentloaded")
            search_box = await page.wait_for_selector("input[name='q']", timeout=10000)
            await search_box.fill(f"test search number {i+1} random {re.sub(r'[^0-9]', '', str(pytest.__version__))}")
            await page.keyboard.press("Enter")
            try:
                await page.wait_for_selector(".b_algo", timeout=10000)
            except:
                pass
            await page.wait_for_timeout(3000)  # Wait for quota update on backend

        # Check quota
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")
        new_quota = await self._get_search_quota_from_dashboard(page)
        
        # Use >= because other searches might be happening or multiple points might be awarded
        assert new_quota >= initial_quota + 3, f"Expected at least +3 searches, got {new_quota} from {initial_quota}"

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(90)
    async def test_search_points_awarded(self, page: Page):
        """
        Verify that search points are awarded (may depend on account level/promotions).
        Note: Points awarding can be delayed; this test is informational.
        """
        pytest.skip("Points awarding is account-specific and may not be immediate; used as integration check only")
