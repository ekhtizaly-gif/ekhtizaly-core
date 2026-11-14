import asyncio
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
from config.settings import SCREENSHOTS_DIR, HEADLESS_MODE, BROWSER_TIMEOUT_MS

class EkhtizalyBrowserRuntime:
    """
    Ekhtizaly Autonomous Core - Browser Execution & Vision Runtime.
    Drives headless Chromium, performs complex user actions (clicking, filling, scrolling),
    and captures visual viewport screenshots for AI analysis.
    """

    def __init__(self):
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir = SCREENSHOTS_DIR

    async def execute_task(self, url: str, action_type: str = "navigate", selector: Optional[str] = None, text: Optional[str] = None, capture_screenshot: bool = True) -> Dict[str, Any]:
        """Executes a browser automation command and optionally captures screenshot."""
        start_time = time.time()
        screenshot_path = None
        
        async with async_playwright() as p:
            browser: Browser = await p.chromium.launch(
                headless=HEADLESS_MODE,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page: Page = await context.new_page()

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT_MS)
                
                # Perform requested action
                if action_type == "click" and selector:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                elif action_type == "fill" and selector and text:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.fill(selector, text)
                elif action_type == "scroll":
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(1)

                page_title = await page.title()

                # Visual capture
                if capture_screenshot:
                    filename = f"capture_{uuid.uuid4().hex[:10]}.png"
                    target_file = self.screenshots_dir / filename
                    await page.screenshot(path=str(target_file), full_page=False)
                    screenshot_path = str(target_file)

                elapsed_ms = (time.time() - start_time) * 1000.0
                await browser.close()

                return {
                    "status": "SUCCESS",
                    "url": url,
                    "title": page_title,
                    "action_executed": action_type,
                    "screenshot_path": screenshot_path,
                    "elapsed_ms": round(elapsed_ms, 2)
                }

            except Exception as e:
                await browser.close()
                return {
                    "status": "ERROR",
                    "url": url,
                    "error": str(e),
                    "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
                }

browser_runtime = EkhtizalyBrowserRuntime()
