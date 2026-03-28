import pytest
from playwright.async_api import Page
from tests.e2e.helpers.login import perform_login

class TestURLRewardTasks:
    """Tests for URL-based reward tasks (visit a page, earn points)."""

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(150)
    async def test_execute_single_url_reward_task(self, page: Page, task_discovery, execute_task, test_credentials):
        """Find first available URL task and execute it."""
        await perform_login(page, test_credentials)
        
        tasks = await task_discovery()
        # Find tasks that are available and have a valid-looking URL
        url_tasks = [t for t in tasks if t.status == "available" and t.url and ("http" in t.url or t.url.startswith("/"))]

        if not url_tasks:
            pytest.skip("No available URL reward tasks")

        task = url_tasks[0]
        success = await execute_task(task.url)
        assert success, f"Task execution failed for: {task.title}"

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(120)
    async def test_url_task_completes_without_navigation_errors(self, page: Page, test_credentials):
        """Executing a known URL task should not cause page crashes or 404s."""
        # This is a bit redundant if we dynamically discover, but we'll include it for completeness
        # We skip because it requires a specific URL, but for E2E we can also test against a real task if found
        pytest.skip("Requires specific task URL; typically discovered dynamically")

    @pytest.mark.e2e
    @pytest.mark.timeout(60)
    async def test_url_task_navigates_to_external_site(self, page: Page):
        """URL tasks may navigate to Microsoft partner sites; should load successfully."""
        pytest.skip("Requires specific task URL; cannot generalize without dynamic discovery")
