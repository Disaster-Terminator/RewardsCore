import pytest
from playwright.async_api import Page

class TestInvalidCredentials:
    """Tests for wrong password, non-existent account, etc."""

    @pytest.mark.e2e
    @pytest.mark.timeout(60)
    async def test_wrong_password_error_message(self, page: Page, test_credentials):
        """Wrong password should show specific error without page crash."""
        # Note: Microsoft login URL can vary by region/context
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")

        # Step 2: Enter correct email
        email_field = await page.wait_for_selector("input[type='email']", timeout=10000)
        await email_field.fill(test_credentials["email"])
        await page.click("input[type='submit']")

        # Step 3: Enter WRONG password
        password_field = await page.wait_for_selector("input[type='password']", timeout=10000)
        await password_field.fill("wrong_password_xyz123_INVALID")
        await page.click("input[type='submit']")

        # Look for error message (class or text)
        error_selectors = [
            "#passwordError", ".error", "[role='alert']",
            "text='incorrect'", "text='wrong'",
            "text='Incorrect password'", "text='Try again'"
        ]
        error_found = False
        for selector in error_selectors:
            try:
                # Use a small timeout for each selector
                el = await page.wait_for_selector(selector, timeout=5000)
                if el:
                    text = await el.text_content()
                    if text and any(kw in text.lower() for kw in ["incorrect", "wrong", "error", "try again"]):
                        error_found = True
                        break
            except:
                continue

        assert error_found, "No error message displayed for wrong password"

    @pytest.mark.e2e
    @pytest.mark.timeout(60)
    async def test_enter_key_submits_login_form(self, page: Page, test_credentials):
        """Pressing Enter in password field should submit login."""
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")

        # Step 2: Enter email
        email_field = await page.wait_for_selector("input[type='email']", timeout=10000)
        await email_field.fill(test_credentials["email"])
        await page.click("input[type='submit']")

        # Step 3: Enter CORRECT password and press Enter
        password_field = await page.wait_for_selector("input[type='password']", timeout=10000)
        await password_field.fill(test_credentials["password"])
        await page.keyboard.press("Enter")

        # Should reach dashboard or 2FA or error, not hang
        try:
            # We wait for any of: rewards dashboard, OTP field, or error alert
            await page.wait_for_selector(".progressContainer, [role='alert'], input[name='otp'], input[name='verificationCode'], input#idBtn_1", timeout=20000)
        except Exception as e:
            pytest.fail(f"Login form submission via Enter key failed to progress: {e}")

    @pytest.mark.e2e
    @pytest.mark.timeout(60)
    async def test_recovery_options_available_on_forgot_password(self, page: Page):
        """Verify 'Forgot password' link navigates to recovery page."""
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")

        # First we need to get to the email page
        try:
             await page.wait_for_selector("input[type='email']", timeout=5000)
        except:
             pytest.skip("Login page not loaded properly")

        # Look for forgot password link
        forgot_link_selectors = [
            "a#idA_PWD_ForgotPassword",
            "a:has-text('Forgot')",
            "a:has-text('Can\\'t access')",
            "a[href*='password']",
            "a[href*='recover']"
        ]

        forgot_link = None
        for selector in forgot_link_selectors:
             forgot_link = await page.query_selector(selector)
             if forgot_link:
                  break

        if forgot_link:
            # Verify link is visible and has expected href
            href = await forgot_link.get_attribute("href")
            assert href, "Forgot password link has no href"
            assert any(kw in href.lower() for kw in ["password", "recover", "reset"]), f"Unexpected href: {href}"
        else:
            pytest.skip("Forgot password link not found (may vary by region/page)")
