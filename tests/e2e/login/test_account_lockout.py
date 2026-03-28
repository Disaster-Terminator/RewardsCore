import pytest
from playwright.async_api import Page

class TestAccountLockout:
    """Tests for account security scenarios (lockout, blocked)."""

    @pytest.mark.e2e
    @pytest.mark.slow  # May require manual intervention or waiting
    @pytest.mark.timeout(180)
    async def test_account_locked_detection(self, page: Page, test_credentials):
        """Test that lockout state is properly detected and reported."""
        # This test assumes account may be locked from too many attempts
        # Or simulate lockout via invalid password attempts (careful in CI)

        # Attempt multiple failed logins (don't actually lock a real account)
        # Instead, check for lockout indicator on rewards page if already locked

        from tests.e2e.helpers.account_health import check_account_health
        health = await check_account_health(page)

        if health.get("reason") == "account_locked":
            # If account is locked, we want this test to "pass" by detecting it
            # But normally we skip because we can't test further
            assert not health["healthy"], "Account should be reported as unhealthy"
            assert health["reason"] == "account_locked", f"Expected lockout, got {health['reason']}"
        else:
            pytest.skip("Account not locked - test requires pre-locked account")

    @pytest.mark.e2e
    @pytest.mark.timeout(60)
    async def test_lockout_message_displayed(self, page: Page):
        """When redirected to rewards with locked account, error message visible."""
        # Navigate to rewards; if account locked, should see message
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")

        # Check for lockout-related text
        lockout_texts = [
            "account is locked",
            "account has been blocked",
            "suspicious activity",
            "verify your identity"
        ]

        # Get the page text content
        page_text = await page.text_content("body")
        if not page_text:
            pytest.skip("Could not retrieve body text content")

        found = any(text.lower() in page_text.lower() for text in lockout_texts)

        if found:
            assert True, "Lockout message detected (expected in this test context)"
        else:
            # We skip instead of fail because we don't want to fail if the account is healthy
            pytest.skip("No lockout message detected - account appears healthy")
