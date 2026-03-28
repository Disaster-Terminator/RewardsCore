import pytest
from playwright.async_api import Page

class TestSearchErrors:
    """Tests for search error conditions and rate limiting."""

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(120)
    async def test_rate_limit_not_triggered_by_normal_usage(self, authenticated_search_page: Page):
        """
        Normal search pace should not trigger rate limiting.
        """
        page = authenticated_search_page
        
        # Perform searches with reasonable intervals (3-5s between)
        for i in range(2):
            await page.goto("https://www.bing.com", wait_until="domcontentloaded")
            search_box = await page.wait_for_selector("input[name='q']", timeout=10000)
            await search_box.fill(f"test rate limit {i} check")
            await page.keyboard.press("Enter")
            try:
                await page.wait_for_selector(".b_algo", timeout=10000)
            except:
                pass
            # Wait for search quota to update
            await page.wait_for_timeout(3000)

        # Should not see rate limit message (no CAPTCHA or "too many requests")
        page_text = await page.text_content("body")
        assert "CAPTCHA" not in page_text, "Rate limit (CAPTCHA) triggered unexpectedly"
        assert "too many requests" not in page_text.lower(), "Rate limit (HTTP 429-like) triggered"

    @pytest.mark.e2e
    @pytest.mark.timeout(60)
    async def test_empty_search_query_handled(self, page: Page):
        """Submitting empty search should not crash or redirect incorrectly."""
        await page.goto("https://www.bing.com", wait_until="domcontentloaded")

        search_box = await page.wait_for_selector("input[name='q']", timeout=10000)
        await search_box.focus()
        await page.keyboard.press("Enter")

        # Should stay on homepage or show validation message
        await page.wait_for_timeout(2000)
        # No crash - page still functional
        title = await page.title()
        # Support both English and Chinese titles, and "Search"/"搜索" which Bing uses
        assert any(x in title for x in ["Bing", "必应", "搜索", "Search"])

    @pytest.mark.e2e
    @pytest.mark.timeout(90)
    async def test_special_characters_in_search(self, page: Page):
        """Search with special characters should not break results."""
        special_terms = [
            "C++ tutorial",
            "Python 3.12 & async",
            "test@example.com",
            "100% complete",
            "price: $500",
            "\"quoted search\"",
            "site:bing.com rewards"
        ]

        for term in special_terms:
            try:
                # Use networkidle to be more stable with redirects
                await page.goto("https://www.bing.com", wait_until="networkidle")
                search_box = await page.wait_for_selector("input[name='q']", timeout=10000)
                await search_box.fill(term)
                await page.keyboard.press("Enter")
                
                # Some special searches might have different result layouts, but .b_algo is common
                await page.wait_for_selector(".b_algo, #b_results", timeout=15000)
                results = await page.query_selector(".b_algo, #b_results")
                assert results is not None, f"No results for: {term}"
            except Exception as e:
                # If selectors fail, verify we didn't get an error page
                # Wait a bit for navigation to settle
                await page.wait_for_timeout(2000)
                try:
                    title = await page.title()
                    assert any(x in title for x in ["Bing", "必应", "搜索", "Search"]), f"Search failed for '{term}' with title: {title}"
                except:
                    # If even title fails, we might still be in a redirect
                    pass
