import pytest
from playwright.async_api import Page
from tests.e2e.helpers.login import perform_login

class TestTaskPersistence:
    """Tests for task state persistence across sessions."""

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(180)
    async def test_completed_task_remains_completed(self, page: Page, task_discovery, execute_task, test_credentials):
        """After completing a task, it should show as completed on refresh."""
        await perform_login(page, test_credentials)
        
        tasks_before = await task_discovery()
        available_tasks = [t for t in tasks_before if t.status == "available" and t.url]

        if not available_tasks:
            pytest.skip("No tasks to complete")

        # Execute first available task
        task = available_tasks[0]
        # Use execute_task fixture instead of direct page.goto to handle potential completion steps
        success = await execute_task(task.url)
        assert success, f"Failed to execute task: {task.title}"

        # Navigate back to dashboard or refresh if redirected
        if "rewards.bing.com" not in page.url:
            await page.goto("https://rewards.bing.com", wait_until="domcontentloaded")
        else:
            await page.reload(wait_until="domcontentloaded")
            
        tasks_after = await task_discovery()

        # Find the same task (by title or URL) and verify status is now completed
        # Note: titles might slightly change (e.g., checkmark added), so we check for title inclusion or URL match
        same_task = next((t for t in tasks_after if (t.url == task.url or task.title in t.title)), None)
        if same_task:
            assert same_task.status == "completed", f"Task {task.title} still shows as {same_task.status}"
        else:
            # Some tasks disappear from the list once completed
            pytest.skip(f"Task {task.title} no longer appears in list after completion, which is a form of completion indicator")

    @pytest.mark.e2e
    @pytest.mark.requires_login
    @pytest.mark.timeout(90)
    async def test_task_list_reflects_current_state(self, page: Page, test_credentials):
        """Task list should update without full page reload after task completion."""
        # This requires more complex mocking or specific timing, so we skip for now
        pytest.skip("Requires implementing partial refresh detection; optional")
