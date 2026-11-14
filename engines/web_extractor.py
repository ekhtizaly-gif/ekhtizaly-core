import asyncio
import time
from typing import Dict, Any, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from security.stealth_limiter import stealth_limiter

class EkhtizalyWebExtractor:
    """
    Ekhtizaly Autonomous Core - High-Performance Web Data Extractor.
    Combines Crawl4AI high-speed asynchronous engine with advanced stealth
    anti-bot bypass to transform web pages into clean, structured Markdown.
    """

    def __init__(self):
        self.browser_cfg = BrowserConfig(
            headless=True,
            verbose=False,
            extra_args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
        )
        self.run_cfg = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=10,
            excluded_tags=["nav", "footer", "aside", "script", "style"]
        )

    async def extract_markdown(self, url: str) -> Dict[str, Any]:
        """Extracts sanitized markdown content and metadata from the target URL."""
        stealth_limiter.enforce_rate_limit(url)
        start_time = time.time()

        try:
            async with AsyncWebCrawler(config=self.browser_cfg) as crawler:
                result = await crawler.arun(url=url, config=self.run_cfg)
                elapsed_ms = (time.time() - start_time) * 1000.0

                if result.success:
                    return {
                        "status": "SUCCESS",
                        "url": url,
                        "title": result.metadata.get("title", "") if result.metadata else "",
                        "markdown": result.markdown,
                        "text_length": len(result.markdown or ""),
                        "links_count": len(result.links.get("internal", []) + result.links.get("external", [])) if result.links else 0,
                        "elapsed_ms": round(elapsed_ms, 2)
                    }
                else:
                    return {
                        "status": "FAILED",
                        "url": url,
                        "error": result.error_message or "Extraction failed",
                        "elapsed_ms": round(elapsed_ms, 2)
                    }
        except Exception as e:
            return {
                "status": "ERROR",
                "url": url,
                "error": str(e),
                "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
            }

web_extractor = EkhtizalyWebExtractor()
