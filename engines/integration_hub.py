import urllib.request
import urllib.parse
import json
import time
from typing import Dict, Any, Optional
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, N8N_URL

class EkhtizalyIntegrationHub:
    """
    Ekhtizaly Autonomous Core - Universal Automation & Channel Integration Hub.
    Bridges n8n workflows, triggers webhook pipelines, and broadcasts operational
    alerts to Telegram, WhatsApp, and connected enterprise endpoints.
    """

    def __init__(self):
        self.telegram_token = TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = TELEGRAM_CHAT_ID
        self.n8n_url = N8N_URL

    def send_telegram_alert(self, message: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """Dispatches an instant notification to Telegram."""
        target_chat = chat_id or self.telegram_chat_id
        if not self.telegram_token or not target_chat:
            return {"status": "SKIPPED", "reason": "Missing Telegram credentials"}

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": target_chat,
            "text": f"🚀 [Ekhtizaly Core Alert]\n\n{message}",
            "parse_mode": "HTML"
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(url, data=data, headers=headers)

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode())
                return {
                    "status": "SUCCESS" if res_data.get("ok") else "FAILED",
                    "response": res_data,
                    "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
            }

    def trigger_n8n_webhook(self, webhook_path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Triggers an n8n automation workflow via incoming webhook."""
        url = f"{self.n8n_url.rstrip('/')}/webhook/{webhook_path.lstrip('/')}"
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(url, data=data, headers=headers)

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode()
                return {
                    "status": "SUCCESS",
                    "webhook": webhook_path,
                    "response_code": response.status,
                    "content": content[:500],
                    "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "webhook": webhook_path,
                "error": str(e),
                "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
            }

integration_hub = EkhtizalyIntegrationHub()
