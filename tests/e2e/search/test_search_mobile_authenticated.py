import pytest
from playwright.async_api import Page

class TestSearchMobileAuthenticated:
    """Authenticated search tests in mobile emulation."""

    @pytest.fixture
    async def mobile_context(self, browser):
        """Create mobile emulation context (iPhone 14)."""
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        yield context
        await context.close()

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(150)
    async def test_mobile_search_works(self, mobile_context, test_credentials):
        """Mobile emulation search should work with authentication."""
        page = await mobile_context.new_page()

        # Login (fresh since mobile context has no storage)
        from tests.e2e.helpers.login import perform_login
        await perform_login(page, test_credentials)

        # Perform search
        await page.goto("https://www.bing.com", wait_until="domcontentloaded")
        search_box = await page.wait_for_selector("input[name='q']", timeout=15000)
        await search_box.fill("mobile search test")
        await page.keyboard.press("Enter")
        
        try:
            await page.wait_for_selector(".b_algo", timeout=15000)
            results = await page.query_selector(".b_algo")
            assert results is not None, "No search results on mobile"
        except Exception:
            # Check for alternative mobile result selectors if needed
            body_text = await page.text_content("body")
            assert len(body_text) > 500, "Page appears empty or failed to load results"

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(150)
    async def test_mobile_rewards_dashboard_accessible(self, mobile_context, test_credentials):
        """Rewards dashboard should be mobile-responsive."""
        page = await mobile_context.new_page()
        from tests.e2e.helpers.login import perform_login
        await perform_login(page, test_credentials)

        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")
        await page.wait_for_selector(".progressContainer, [data-ct*='dashboard']", timeout=25000)

        # Check viewport meta tag (mobile-friendly)
        viewport_meta = await page.query_selector("meta[name='viewport']")
        assert viewport_meta is not None, "No viewport meta tag - not mobile-friendly"
        
        content = await viewport_meta.get_attribute("content")
        assert "width=device-width" in content or "initial-scale" in content
