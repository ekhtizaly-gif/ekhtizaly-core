from fastmcp import FastMCP
from typing import Dict, Any
import json
from engines.integration_hub import integration_hub

mcp = FastMCP("Ekhtizaly-Automation-Server")

@mcp.tool()
async def trigger_n8n_flow(webhook_path: str, payload_json: str) -> Dict[str, Any]:
    """Triggers an n8n webhook workflow with JSON payload data."""
    try:
        data = json.loads(payload_json) if isinstance(payload_json, str) else payload_json
    except Exception:
        data = {"raw": payload_json}
    return integration_hub.trigger_n8n_webhook(webhook_path=webhook_path, payload=data)

@mcp.tool()
async def send_telegram_notification(message: str) -> Dict[str, Any]:
    """Sends an instant alert message to the configured administrative Telegram channel."""
    return integration_hub.send_telegram_alert(message=message)

@mcp.tool()
async def dispatch_multi_channel_alert(title: str, body: str) -> Dict[str, Any]:
    """Dispatches formatted notification across active broadcast channels."""
    msg = f"<b>{title}</b>\n\n{body}"
    res = integration_hub.send_telegram_alert(message=msg)
    return {
        "status": "DISPATCHED",
        "channels": ["TELEGRAM"],
        "telegram_delivery": res.get("status")
    }

server = mcp
