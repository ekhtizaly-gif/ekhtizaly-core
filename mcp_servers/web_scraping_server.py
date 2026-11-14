from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
from engines.web_extractor import web_extractor

mcp = FastMCP("Ekhtizaly-Web-Extraction-Server")

@mcp.tool()
async def extract_clean_markdown(url: str) -> Dict[str, Any]:
    """Extracts clean, noise-free Markdown content from any target website."""
    return await web_extractor.extract_markdown(url)

@mcp.tool()
async def extract_structured_fields(url: str, fields: List[str]) -> Dict[str, Any]:
    """Extracts page text and maps key fields from the target webpage."""
    raw = await web_extractor.extract_markdown(url)
    if raw.get("status") != "SUCCESS":
        return raw
    
    md_text = raw.get("markdown", "")
    extracted = {}
    for f in fields:
        f_lower = f.lower()
        lines = [line.strip() for line in md_text.split("\n") if f_lower in line.lower()]
        extracted[f] = lines[:3] if lines else "Not detected"

    return {
        "status": "SUCCESS",
        "url": url,
        "fields": extracted,
        "raw_text_length": len(md_text)
    }

@mcp.tool()
async def crawl_multiple_urls(urls: List[str]) -> List[Dict[str, Any]]:
    """Crawls and extracts markdown from multiple URLs in parallel."""
    tasks = [web_extractor.extract_markdown(u) for u in urls[:5]]
    return await asyncio.gather(*tasks)

server = mcp
