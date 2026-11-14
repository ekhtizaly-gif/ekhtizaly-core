import asyncio
import re
import time
from typing import Dict, Any, Optional
from engines.web_extractor import web_extractor
from engines.browser_runtime import browser_runtime
from memory.semantic_vault import vault
from engines.integration_hub import integration_hub

class EkhtizalyPriceSentinelWorkflow:
    """
    Ekhtizaly Autonomous Core - E-Commerce & Asset Price Sentinel.
    Autonomously tracks competitor product pricing, captures proof-of-state screenshots,
    detects threshold anomalies, and alerts operators immediately.
    """

    PRICE_PATTERN = re.compile(r"(\$|€|£|USD|SAR|AED)\s*([0-9]+(?:[\.,][0-9]{2})?)")

    async def execute(self, target_url: str, item_name: str, threshold_price: Optional[float] = None) -> Dict[str, Any]:
        start_time = time.time()

        # 1. High-speed content extraction
        extract_res = await web_extractor.extract_markdown(target_url)
        markdown = extract_res.get("markdown", "") if extract_res.get("status") == "SUCCESS" else ""

        # 2. Extract price candidates
        matches = self.PRICE_PATTERN.findall(markdown)
        found_prices = []
        for currency, val_str in matches:
            try:
                num = float(val_str.replace(",", ""))
                found_prices.append((currency, num))
            except ValueError:
                continue

        detected_min = min([p[1] for p in found_prices]) if found_prices else None
        detected_currency = found_prices[0][0] if found_prices else "USD"

        # 3. Capture visual verification screenshot
        browser_res = await browser_runtime.execute_task(url=target_url, action_type="navigate", capture_screenshot=True)
        screenshot = browser_res.get("screenshot_path")

        # 4. Anomaly detection & Alerting
        alert_triggered = False
        if threshold_price and detected_min and detected_min <= threshold_price:
            alert_triggered = True
            msg = f"📉 <b>Price Drop Detected!</b>\nItem: {item_name}\nCurrent Price: {detected_currency} {detected_min}\nThreshold: {threshold_price}\nLink: {target_url}"
            integration_hub.send_telegram_alert(msg)

        # 5. Store in Vault
        doc_content = f"Item: {item_name}\nURL: {target_url}\nDetected Price: {detected_min}\nAlert: {alert_triggered}"
        vault.store_document(
            doc_id=f"price_{int(time.time())}",
            title=f"Price Sentinel: {item_name}",
            content=doc_content,
            category="price_sentinel",
            metadata={"url": target_url, "price": detected_min, "screenshot": screenshot}
        )

        return {
            "status": "SUCCESS",
            "item_name": item_name,
            "target_url": target_url,
            "detected_price": detected_min,
            "currency": detected_currency,
            "alert_triggered": alert_triggered,
            "screenshot_path": screenshot,
            "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
        }

price_sentinel = EkhtizalyPriceSentinelWorkflow()
