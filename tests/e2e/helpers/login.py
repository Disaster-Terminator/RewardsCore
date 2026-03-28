from playwright.async_api import Page
from tests.e2e.helpers.totp import fill_totp_code

async def perform_login(page: Page, credentials: dict):
    """
    Perform complete login flow:
    1. Navigate to rewards.bing.com (triggers redirect to login)
    2. Enter email
    3. Enter password
    4. Handle 2FA if configured
    5. Handle stay-signed-in
    6. Verify redirected to rewards dashboard
    """
    # Step 1: Navigate to rewards triggers login
    await page.goto("https://rewards.bing.com", wait_until="domcontentloaded", timeout=30000)

    # Step 2: Enter email
    email_field = await page.wait_for_selector("input[type='email']", timeout=10000)
    await email_field.fill(credentials["email"])
    await page.click("input[type='submit']")

    # Step 3: Enter password
    password_field = await page.wait_for_selector("input[type='password']", timeout=10000)
    await password_field.fill(credentials["password"])
    await page.click("input[type='submit']")

    # Step 4: Handle 2FA if TOTP secret provided
    if credentials.get("totp_secret"):
        try:
            # Wait a bit for the 2FA page to load
            await page.wait_for_timeout(2000)
            await fill_totp_code(page, credentials["totp_secret"])
            await page.click("input[type='submit']")
        except Exception as e:
            # 2FA field not found - maybe not required for this account
            print(f"DEBUG: TOTP skip/fail: {e}")
            pass

    # Step 5: Stay signed in prompt (look for "Yes" / "No")
    try:
        await page.wait_for_selector("input#idBtn_1", timeout=5000)  # "Yes" button
        await page.click("input#idBtn_1")
    except:
        pass  # No prompt, continue

    # Step 6: Verify reached rewards dashboard
    try:
        await page.wait_for_url("https://rewards.bing.com/**", timeout=30000)
    except:
        pass # Sometimes it might already be there or on a slightly different URL

    dashboard = await page.query_selector(".progressContainer, [data-ct*='dashboard']")
    if not dashboard:
        # Final attempt to check if we are on dashboard
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")
        dashboard = await page.query_selector(".progressContainer, [data-ct*='dashboard']")

    assert dashboard is not None, "Login failed - dashboard not reached"
