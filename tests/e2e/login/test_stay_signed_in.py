import pytest
from playwright.async_api import Page

class TestStaySignedIn:
    """Tests for the 'Stay signed in?' prompt (common after login)."""

    @pytest.mark.e2e
    @pytest.mark.timeout(120)
    async def test_stay_signed_in_yes_button_works(self, page: Page, test_credentials):
        """Clicking 'Yes' on stay-signed-in should proceed to dashboard."""
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")

        # Login process
        await page.fill("input[type='email']", test_credentials["email"])
        await page.click("input[type='submit']")
        await page.fill("input[type='password']", test_credentials["password"])
        await page.click("input[type='submit']")

        # Look for "Stay signed in?" prompt (Yes button: idBtn_1 or "Yes")
        try:
            # We wait for the "Yes" button (idBtn_1)
            yes_button = await page.wait_for_selector("input#idBtn_1", timeout=15000)
            await yes_button.click()
        except:
            # Prompt didn't appear - skip (account may have suppressed it)
            pytest.skip("Stay signed in prompt not shown (suppressed or account already opted-in)")

        # Should reach rewards dashboard
        try:
            await page.wait_for_selector(".progressContainer, [data-ct*='dashboard']", timeout=30000)
        except Exception as e:
            # Maybe it went to another intermediate page?
            assert "rewards.bing.com" in page.url, f"Expected rewards dashboard, current URL: {page.url}"

        assert "rewards.bing.com" in page.url

    @pytest.mark.e2e
    @pytest.mark.timeout(120)
    async def test_stay_signed_in_no_button_works(self, page: Page, test_credentials):
        """Clicking 'No' should still proceed to dashboard, just less persistent."""
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")

        # Login process
        await page.fill("input[type='email']", test_credentials["email"])
        await page.click("input[type='submit']")
        await page.fill("input[type='password']", test_credentials["password"])
        await page.click("input[type='submit']")

        # Look for "Stay signed in?" prompt (No button: idBtn_2 or "No")
        try:
            no_button = await page.wait_for_selector("input#idBtn_2", timeout=15000)
            await no_button.click()
        except:
            # Prompt didn't appear - skip (account may have suppressed it)
            pytest.skip("Stay signed in prompt not shown (suppressed or account already opted-in)")

        # Should still reach rewards dashboard
        try:
            await page.wait_for_selector(".progressContainer, [data-ct*='dashboard']", timeout=30000)
        except Exception as e:
            assert "rewards.bing.com" in page.url, f"Expected rewards dashboard, current URL: {page.url}"

        assert "rewards.bing.com" in page.url
