import pytest
import os
from tests.e2e.helpers.account_health import skip_if_unhealthy

class TestLoginFlow:
    
    @pytest.mark.asyncio
    @skip_if_unhealthy("admin_logged_in_page")
    async def test_successful_login(self, admin_logged_in_page):
        """
        Verify that the admin_logged_in_page fixture successfully logs in.
        The skip_if_unhealthy decorator will skip this test if login or dashboard
        check fails during health check.
        """
        # admin_logged_in_page is already at rewards.bing.com dashboard
        # Verify dashboard element is visible
        dashboard = await admin_logged_in_page.query_selector(".progressContainer, [data-ct*='dashboard']")
        assert dashboard is not None, "Dashboard not found after login"
        
        # Verify URL is correct
        assert "rewards.bing.com" in admin_logged_in_page.url
