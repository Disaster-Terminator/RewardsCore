import pytest
import os
import json
import re
from typing import Dict, Tuple, Callable, Awaitable

def load_search_terms() -> list[str]:
    """Load search terms from data file."""
    # Try current task plan specified path
    path = os.path.join("tests", "e2e", "data", "search_terms.txt")
    if not os.path.exists(path):
        # Fallback to common search terms if task-specific one is missing
        path = os.path.join("tests", "e2e", "data", "common", "search_terms.txt")

    if not os.path.exists(path):
        return ["microsoft rewards", "playwright testing", "python async"]

    with open(path) as f:
        terms = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return terms

@pytest.fixture(params=load_search_terms())
def search_term(request) -> str:
    """Parametrized fixture providing search terms."""
    return request.param

@pytest.fixture
async def authenticated_search_page(page, test_credentials):
    """
    Login and return page ready for authenticated search tests.
    Uses storage state if available for speed; falls back to fresh login.
    """
    # Check if storage state available
    storage_path = os.getenv("E2E_STORAGE_STATE", "tests/fixtures/storage_state.json")
    if os.path.exists(storage_path):
        # Add cookies to current context
        with open(storage_path) as f:
            storage_state = json.load(f)
        await page.context.add_cookies(storage_state.get("cookies", []))
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")
    else:
        # Perform fresh login
        from tests.e2e.helpers.login import perform_login
        await perform_login(page, test_credentials)

    # Verify dashboard accessible
    await page.wait_for_selector(".progressContainer, [data-ct*='dashboard']", timeout=15000)
    return page

@pytest.fixture
async def search_with_points_check(authenticated_search_page) -> Tuple[pytest.fixture, Callable[[], Awaitable[int]]]:
    """
    Return page and provide helper to check/search for points changes.
    """
    page = authenticated_search_page

    async def get_current_points() -> int:
        """Parse points from dashboard or header."""
        # Try various selectors
        selectors = [
            ".credits_value",  # Dashboard points
            "[data-ct*='points']",
            ".mee-textPoints",
            "span[aria-label*='point']"
        ]
        for selector in selectors:
            el = await page.query_selector(selector)
            if el:
                text = await el.text_content()
                if not text:
                    continue
                # Extract number from "1,234 points" or "1234"
                match = re.search(r'[\d,]+', text.replace(',', ''))
                if match:
                    return int(match.group())
        return 0

    return page, get_current_points
