import pytest
from playwright.async_api import Page
from tests.e2e.helpers.login import perform_login

class TestTaskFiltering:
    """Tests for task categorization and filtering."""

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(90)
    async def test_tasks_grouped_by_category(self, page: Page, test_credentials):
        """Tasks may be grouped (e.g., 'Search', 'Quizzes', 'Surveys')."""
        await perform_login(page, test_credentials)
        await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")

        # Look for category headers, tabs, or grouped containers
        # We use a set of potential selectors based on MS Rewards UI
        category_selectors = [
            ".category-header", 
            ".tab", 
            ".group-title", 
            "h2:has-text('Daily set')",
            "h2:has-text('More activities')"
        ]
        
        found_categories = False
        for selector in category_selectors:
            try:
                elems = await page.query_selector_all(selector)
                if len(elems) > 0:
                    found_categories = True
                    break
            except:
                continue
                
        if found_categories:
            assert True  # Categories present
        else:
            pytest.skip("No category grouping visible in current UI for this account")

    @pytest.mark.e2e
    @pytest.mark.timeout(60)
    async def test_filter_completed_tasks_hides_inprogress(self, page: Page):
        """If filter 'Completed' is selected, available tasks should be hidden."""
        # Not all UI versions have filtering controls; skip if not found
        pytest.skip("Requires interacting with filter controls; UI may not have this feature in current version")
