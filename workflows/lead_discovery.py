import asyncio
import time
import uuid
from typing import Dict, Any, List
from engines.intelligence_radar import intelligence_radar
from memory.semantic_vault import vault
from engines.integration_hub import integration_hub

class EkhtizalyLeadDiscoveryWorkflow:
    """
    Ekhtizaly Autonomous Core - High-Value Lead & Market Discovery Workflow.
    Autonomously scans open ecosystems, identifies active developer demands,
    calculates commercial fit, and indexes prioritized leads into the vault.
    """

    async def execute(self, keyword: str = "mcp servers ai", limit: int = 5) -> Dict[str, Any]:
        start_time = time.time()
        res = intelligence_radar.search_github_repositories(query=keyword, limit=limit)
        
        if res.get("status") != "SUCCESS":
            return {"status": "FAILED", "error": res.get("error", "Failed to query intelligence radar")}

        harvested_leads = []
        for item in res.get("items", []):
            name = item.get("name", "")
            stars = item.get("stars", 0)
            forks = item.get("forks", 0)
            url = item.get("url", "")
            desc = item.get("description", "")

            # Commercial demand score
            lead_score = round(min(100.0, (stars * 0.05) + (forks * 0.2)), 2)
            lead_id = f"lead_{uuid.uuid4().hex[:8]}"

            lead_data = {
                "repository": name,
                "stars": stars,
                "forks": forks,
                "description": desc,
                "url": url,
                "score": lead_score,
                "discovery_keyword": keyword
            }

            vault.store_lead(
                lead_id=lead_id,
                source="GITHUB_RADAR",
                title=f"Developer Demand: {name}",
                url=url,
                data=lead_data,
                score=lead_score
            )

            harvested_leads.append(lead_data)

        # Notify admin if high-value leads discovered
        if harvested_leads and harvested_leads[0]["score"] > 50:
            top_lead = harvested_leads[0]
            alert_msg = f"🎯 High-Value Opportunity Found: <b>{top_lead['repository']}</b>\n⭐ Stars: {top_lead['stars']} | Score: {top_lead['score']}\n🔗 {top_lead['url']}"
            integration_hub.send_telegram_alert(alert_msg)

        return {
            "status": "SUCCESS",
            "keyword": keyword,
            "leads_discovered": len(harvested_leads),
            "leads": harvested_leads,
            "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
        }

lead_discovery = EkhtizalyLeadDiscoveryWorkflow()
