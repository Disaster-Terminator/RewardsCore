import json
import os
import logging
from datetime import datetime
from playwright.async_api import Page

logger = logging.getLogger(__name__)

async def save_login_diagnostic(page: Page, test_name: str, **kwargs):
    """
    Save diagnostic data on login test failure.
    Captured data includes:
    - Screenshot (if possible)
    - Page URL
    - Page title
    - Any additional metadata provided
    """
    # Ensure diagnostic logs directory exists
    logs_dir = os.path.join(os.getcwd(), "logs", "e2e", "login_diagnostics")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Ensure screenshots directory exists
    screenshots_dir = os.path.join(os.getcwd(), "logs", "e2e", "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{test_name}_{timestamp}"
    
    # Save metadata to JSON
    json_path = os.path.join(logs_dir, f"{base_filename}.json")
    
    data = {
        "test": test_name,
        "timestamp": timestamp,
        "url": page.url,
        "title": await page.title(),
        **kwargs
    }

    try:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Diagnostic metadata saved to {json_path}")
    except Exception as e:
        logger.error(f"Failed to save diagnostic metadata to {json_path}: {e}")

    # Capture screenshot
    screenshot_path = os.path.join(screenshots_dir, f"{base_filename}.png")
    try:
        if not page.is_closed():
            await page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Diagnostic screenshot saved to {screenshot_path}")
    except Exception as e:
        logger.error(f"Failed to capture diagnostic screenshot: {e}")

    return {
        "metadata_path": json_path,
        "screenshot_path": screenshot_path
    }
