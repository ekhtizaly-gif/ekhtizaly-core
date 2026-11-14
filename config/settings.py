import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ==============================================================================
# Ekhtizaly Autonomous Core v2.0 - Configuration Settings
# Proprietary Autonomous Agent & Universal Automation Platform
# ==============================================================================

PLATFORM_NAME = "Ekhtizaly Autonomous Core"
PLATFORM_CODE = "EKHTIZALY_CORE"
PLATFORM_VERSION = "2.0.0-PROD"
ORGANIZATION = "Ekhtizaly Intelligence Systems"

# Gateway Network Settings
GATEWAY_HOST = os.getenv("EKHTIZALY_HOST", "0.0.0.0")
GATEWAY_PORT = int(os.getenv("EKHTIZALY_PORT", "8090"))

# Persistent Database & Storage Path
DATABASE_PATH = os.getenv("EKHTIZALY_DB_PATH", str(BASE_DIR / "data" / "ekhtizaly_vault.db"))
SCREENSHOTS_DIR = BASE_DIR / "data" / "screenshots"

# Communications & Notifications
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WHATSAPP_GATEWAY_URL = os.getenv("WHATSAPP_GATEWAY_URL", "http://127.0.0.1:3000/api/whatsapp")

# Web3 & Blockchain Audit Settings
EVM_WALLET = os.getenv("EVM_WALLET", "0x0000000000000000000000000000000000000000")
DEFAULT_EVM_RPC = os.getenv("DEFAULT_EVM_RPC", "https://mainnet.base.org")

# Automation & Connector Hub
N8N_URL = os.getenv("N8N_URL", "http://127.0.0.1:5678")

# Browser Runtime Settings
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "true").lower() == "true"
BROWSER_TIMEOUT_MS = int(os.getenv("BROWSER_TIMEOUT_MS", "30000"))
