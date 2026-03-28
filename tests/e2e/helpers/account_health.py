from playwright.async_api import Page

async def check_account_health(page: Page) -> dict:
    """
    Check if test account is healthy (not locked, can access rewards).
    Returns: {"healthy": bool, "reason": str if not}
    """
    try:
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded", timeout=15000)

        # Check for lockout indicators
        lockout_selectors = [
            "text='account is locked'",
            "text='account has been blocked'",
            "[data-ct*='locked']",
            ".accountLocked"
        ]
        for selector in lockout_selectors:
            element = await page.query_selector(selector)
            if element:
                text = await element.text_content()
                if text and "lock" in text.lower():
                    return {"healthy": False, "reason": "account_locked", "details": text.strip()}

        # Check for sign-in prompt (means not logged in)
        signin_selectors = [
            "a[href*='login']",
            "button:has-text('Sign in')",
            "text='Sign in'"
        ]
        for selector in signin_selectors:
            element = await page.query_selector(selector)
            if element:
                return {"healthy": False, "reason": "not_logged_in"}

        # Check for home/dashboard elements (logged in)
        dashboard_indicators = [
            ".progressContainer",
            "[data-ct*='dashboard']",
            "text='Daily'"
        ]
        for selector in dashboard_indicators:
            if await page.query_selector(selector):
                return {"healthy": True}

        return {"healthy": False, "reason": "uncertain_state"}
    except Exception as e:
        return {"healthy": False, "reason": "error", "details": str(e)}

def skip_if_unhealthy(page_fixture_name: str = "page"):
    """
    Decorator to skip test if account health check fails.
    Usage: @skip_if_unhealthy() or @skip_if_unhealthy("admin_logged_in_page")
    """
    def decorator(func):
        import pytest
        import functools
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Find page fixture from kwargs
            page = kwargs.get(page_fixture_name)
            if not page:
                # Try to find by type
                for arg in args:
                    if hasattr(arg, 'goto') and hasattr(arg, 'query_selector'):
                        page = arg
                        break
            if page:
                from tests.e2e.helpers.account_health import check_account_health
                health = await check_account_health(page)
                if not health["healthy"]:
                    pytest.skip(f"Account unhealthy: {health['reason']} - {health.get('details', '')}")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Alias for compatibility with existing code
requires_healthy_account = skip_if_unhealthy
