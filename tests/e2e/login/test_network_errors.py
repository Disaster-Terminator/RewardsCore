import pytest
from playwright.async_api import Page, TimeoutError

class TestNetworkErrors:
    """Tests for network failures during login."""

    @pytest.mark.e2e
    @pytest.mark.timeout(180)  # Throttled network is very slow
    async def test_login_with_slow_network(self, page: Page, test_credentials):
        """Simulate slow network (throttling) and verify login still completes."""
        # Set network conditions via CDP session
        context = page.context
        cdp = await context.new_cdp_session(page)
        
        # Simulating a slow 3G network
        # Network.emulateNetworkConditions params: 
        # offline, latency, downloadThroughput, uploadThroughput, connectionType
        await cdp.send("Network.emulateNetworkConditions", {
            "offline": False,
            "latency": 2000,  # 2s latency
            "downloadThroughput": 400 * 1024 // 8,  # 400 Kbps (in bytes)
            "uploadThroughput": 150 * 1024 // 8,    # 150 Kbps
        })

        # Should still succeed (just slower)
        from tests.e2e.helpers.login import perform_login
        try:
            # Re-performing login with throttling
            await perform_login(page, test_credentials)
            assert "rewards.bing.com" in page.url
        except Exception as e:
            pytest.fail(f"Login failed under slow network (latency 2000ms): {e}")
        finally:
            # Reset
            await cdp.send("Network.emulateNetworkConditions", {
                "offline": False,
                "latency": 0,
                "downloadThroughput": -1,
                "uploadThroughput": -1
            })

    @pytest.mark.e2e
    @pytest.mark.timeout(60)
    async def test_login_page_loads_even_with_high_latency(self, page: Page):
        """Microsoft login page should load even with high latency."""
        # Set latency to 5s via CDP
        context = page.context
        cdp = await context.new_cdp_session(page)
        await cdp.send("Network.emulateNetworkConditions", {
            "offline": False,
            "latency": 5000,
            "downloadThroughput": -1,
            "uploadThroughput": -1
        })

        try:
             # Direct navigate to login.live.com
             await page.goto("https://login.live.com", wait_until="domcontentloaded", timeout=45000)
             assert "login.live.com" in page.url

             # Page should be functional - can type in email field
             email_field = await page.wait_for_selector("input[type='email']", timeout=15000)
             assert email_field is not None
             await email_field.fill("test@example.com")
             assert await email_field.input_value() == "test@example.com"
        finally:
             # Reset
             await cdp.send("Network.emulateNetworkConditions", {
                "offline": False,
                "latency": 0,
                "downloadThroughput": -1,
                "uploadThroughput": -1
            })

    @pytest.mark.e2e
    @pytest.mark.timeout(60)
    async def test_error_displayed_when_offline(self, page: Page):
        """When offline, page should show network error, and recover when online again."""
        context = page.context
        
        # Step 1: Go offline
        await context.set_offline(True)

        # Step 2: Try to navigate - should throw
        with pytest.raises(Exception):
             await page.goto("https://login.live.com", wait_until="domcontentloaded", timeout=5000)

        # Step 3: Go back online
        await context.set_offline(False)

        # Step 4: Navigate again - should succeed
        try:
             await page.goto("https://login.live.com", wait_until="domcontentloaded", timeout=30000)
             assert "login.live.com" in page.url
        except:
             pytest.fail("Failed to recover from offline state")
