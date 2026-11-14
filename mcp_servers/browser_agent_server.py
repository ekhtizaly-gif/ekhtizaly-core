from fastmcp import FastMCP
from typing import Dict, Any, Optional
from engines.browser_runtime import browser_runtime

mcp = FastMCP("Ekhtizaly-Browser-Agent-Server")

@mcp.tool()
async def browser_navigate(url: str) -> Dict[str, Any]:
    """Navigates headless Chromium to a target URL and validates loading."""
    return await browser_runtime.execute_task(url=url, action_type="navigate", capture_screenshot=False)

@mcp.tool()
async def browser_click(url: str, selector: str) -> Dict[str, Any]:
    """Clicks on an interactive element by CSS selector on the given URL."""
    return await browser_runtime.execute_task(url=url, action_type="click", selector=selector, capture_screenshot=True)

@mcp.tool()
async def browser_fill(url: str, selector: str, text: str) -> Dict[str, Any]:
    """Fills an input or search field with specified text and captures screen state."""
    return await browser_runtime.execute_task(url=url, action_type="fill", selector=selector, text=text, capture_screenshot=True)

@mcp.tool()
async def browser_screenshot(url: str) -> Dict[str, Any]:
    """Captures a high-resolution screenshot of the target webpage viewport."""
    return await browser_runtime.execute_task(url=url, action_type="navigate", capture_screenshot=True)

server = mcp
