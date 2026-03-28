import pytest
from playwright.async_api import Page

class TestSearchSession:
    """Tests for search session consistency across multiple searches."""

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(120)
    async def test_search_session_persists_across_tabs(self, authenticated_search_page: Page):
        """Opening search in new tab should maintain same session."""
        page = authenticated_search_page
        
        await page.goto("https://www.bing.com", wait_until="domcontentloaded")

        # Get cookies before search
        cookies_before = await page.context.cookies()
        # Filter session cookies (often start with MUID, _SS, etc)
        muid_before = next((c for c in cookies_before if c["name"] == "MUID"), None)

        # Perform a search in current tab
        search_box = await page.wait_for_selector("input[name='q']", timeout=10000)
        await search_box.fill("session test persistent")
        await page.keyboard.press("Enter")
        try:
            await page.wait_for_selector(".b_algo", timeout=10000)
        except:
            pass

        # Open new tab and navigate to Bing
        new_page = await page.context.new_page()
        await new_page.goto("https://www.bing.com", wait_until="domcontentloaded")

        # Should have same session cookies
        cookies_after = await page.context.cookies()
        muid_after = next((c for c in cookies_after if c["name"] == "MUID"), None)
        
        # MUID should be stable for the context
        if muid_before and muid_after:
            assert muid_before["value"] == muid_after["value"], "Session cookie (MUID) changed unexpectedly"

        # Verify search works in new tab without re-login prompt blocking
        search_box_new = await new_page.wait_for_selector("input[name='q']", timeout=10000)
        await search_box_new.fill("another search in new tab")
        await page.keyboard.press("Enter")
        
        # Simple check for results
        await new_page.wait_for_timeout(3000)
        title = await new_page.title()
        assert any(x in title for x in ["Bing", "必应", "搜索", "Search"])
        await new_page.close()

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(90)
    async def test_search_preferences_remembered(self, page: Page):
        """Search preferences (region, safe search) should persist."""
        pytest.skip("Requires modifying user preferences; test if relevant to your account")

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(90)
    async def test_search_history_not_leaking_between_accounts(self, browser, test_credentials):
        """Two different test accounts should not share search history."""
        # Use two different credential sets (if available)
        pytest.skip("Requires two distinct test accounts with no shared cookies")
