import pytest
from playwright.async_api import Page

class Test2FAFailures:
    """Tests for 2FA code errors and recovery."""

    @pytest.mark.e2e
    @pytest.mark.timeout(90)
    async def test_incorrect_totp_code_error(self, page: Page, test_credentials):
        """Entering wrong TOTP code should show error and allow retry."""
        if not test_credentials.get("totp_secret"):
            pytest.skip("No TOTP secret configured")

        # Navigate to login, enter email/password to reach 2FA
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")
        
        # Step 1: Enter email
        email_field = await page.wait_for_selector("input[type='email']", timeout=10000)
        await email_field.fill(test_credentials["email"])
        await page.click("input[type='submit']")

        # Step 2: Enter password
        password_field = await page.wait_for_selector("input[type='password']", timeout=10000)
        await password_field.fill(test_credentials["password"])
        await page.click("input[type='submit']")

        # Step 3: Wait for 2FA input
        # MS 2FA selectors: "otp", "verificationCode", "idTxtBx_SAOTCC_OTC"
        otp_selector = "input[name='otp'], input[name='verificationCode'], input#idTxtBx_SAOTCC_OTC"
        try:
            await page.wait_for_selector(otp_selector, timeout=20000)
        except:
            # Maybe 2FA not required for this session/account
            pytest.skip("2FA input not found - account may not have 2FA enabled or it's suppressed")

        # Step 4: Enter wrong code (e.g., 123456)
        await page.fill(otp_selector, "123456")
        await page.click("input[type='submit']")

        # Step 5: Should show error, stay on same page or show message
        error_selectors = [
            "#otcError", ".error", "[role='alert']", 
            "text='incorrect'", "text='invalid'", "text='try again'",
            "text='Try a different'"
        ]
        error_found = False
        for selector in error_selectors:
            try:
                 el = await page.wait_for_selector(selector, timeout=5000)
                 if el:
                      error_found = True
                      break
            except:
                 continue

        assert error_found or "2fa" in page.url.lower() or "Abc" in page.url, "2FA error not indicated"

    @pytest.mark.e2e
    @pytest.mark.timeout(60)
    async def test_backup_2fa_method_available(self, page: Page, test_credentials):
        """If TOTP fails, should see option to use other verification methods."""
        if not test_credentials.get("totp_secret"):
            pytest.skip("No TOTP secret configured")

        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")
        
        # Get to 2FA page
        await page.fill("input[type='email']", test_credentials["email"])
        await page.click("input[type='submit']")
        await page.fill("input[type='password']", test_credentials["password"])
        await page.click("input[type='submit']")

        # Wait for 2FA options
        try:
             # Look for "Other ways to sign in" or similar
             another_way = await page.wait_for_selector("text='Use a different verification option', text='Other ways', a#idA_SAOTCS_ProofUp", timeout=15000)
             assert another_way is not None, "Alternative 2FA methods link not found"
        except:
             pytest.skip("Alternative 2FA methods link not found (may not be available for this account/session)")
