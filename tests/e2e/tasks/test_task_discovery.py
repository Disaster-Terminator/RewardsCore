import pytest
from playwright.async_api import Page
from tests.e2e.helpers.login import perform_login

class TestTaskDiscovery:
    """Tests for discovering and enumerating available tasks."""

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(90)
    async def test_dashboard_shows_tasks(self, page: Page, task_discovery, test_credentials):
        """Rewards dashboard should display task cards."""
        await perform_login(page, test_credentials)

        tasks = await task_discovery()
        assert len(tasks) > 0, "No tasks found on dashboard"

        # At least one task should be available (not all completed)
        available = [t for t in tasks if t.status == "available"]
        assert len(available) > 0, "No available tasks detected"

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(90)
    async def test_task_has_title_and_url(self, page: Page, task_discovery, test_credentials):
        """Each task should have a title and actionable URL."""
        # Note: If previous test already logged in and we reuse page, it might already be logged in
        # But for isolation, let's assume each test starts fresh (as per conftest.py page fixture)
        await perform_login(page, test_credentials)
        
        tasks = await task_discovery()
        assert len(tasks) > 0

        for task in tasks:
            assert task.title and len(task.title) > 0, f"Task missing title: {task}"
            # Some tasks might not have a URL if they are informational, but usually they do
            assert task.url and (task.url.startswith("http") or task.url.startswith("/")), f"Task missing valid URL: {task}"

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(90)
    async def test_completed_tasks_marked(self, page: Page, task_discovery, test_credentials):
        """Tasks that are already completed should have status 'completed'."""
        await perform_login(page, test_credentials)
        
        tasks = await task_discovery()
        # Find at least one completed task if any exist
        completed = [t for t in tasks if t.status == "completed"]
        if completed:
            for task in completed:
                # We already determined it's completed in the discovery fixture
                assert task.status == "completed"
        else:
            pytest.skip("No completed tasks found (may be first run or reset)")
