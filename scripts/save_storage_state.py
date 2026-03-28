#!/usr/bin/env python
"""
Save storage_state.json after successful login for reuse.
Agent execution (uses conda environment):
    ${CONDA_PREFIX}/bin/python scripts/save_storage_state.py

Manual usage:
    MS_REWARDS_E2E_EMAIL=user@example.com \
    MS_REWARDS_E2E_PASSWORD=secret \
    python scripts/save_storage_state.py
"""
import asyncio
import os
import json
import sys

# Add project root to sys.path to allow importing from src and tests
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
# Also add src to path if needed
sys.path.insert(0, os.path.join(project_root, "src"))

from playwright.async_api import async_playwright
from tests.e2e.helpers.login import perform_login

async def main():
    email = os.getenv("MS_REWARDS_E2E_EMAIL")
    password = os.getenv("MS_REWARDS_E2E_PASSWORD")
    if not email or not password:
        print("ERROR: Set MS_REWARDS_E2E_EMAIL and MS_REWARDS_E2E_PASSWORD")
        return 1

    headless = os.getenv("E2E_HEADLESS", "false").lower() == "true"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        creds = {"email": email, "password": password, "totp_secret": os.getenv("MS_REWARDS_E2E_TOTP_SECRET")}
        try:
            await perform_login(page, creds)
            storage_state = await context.storage_state()
            os.makedirs("tests/fixtures", exist_ok=True)
            with open("tests/fixtures/storage_state.json", "w") as f:
                json.dump(storage_state, f, indent=2)
            print("✅ storage_state.json saved")
            return 0
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return 1
        finally:
            await browser.close()

if __name__ == "__main__":
    exit(asyncio.run(main()))
