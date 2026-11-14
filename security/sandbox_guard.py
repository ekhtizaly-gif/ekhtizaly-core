import re
import os
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger("ekhtizaly_security")

class EkhtizalySecurityGuard:
    """
    Ekhtizaly Core Security & Sandbox Guard.
    Enforces strict command firewalling, credential leak redaction, and infrastructure boundaries.
    """

    DESTRUCTIVE_PATTERNS = [
        r"\brm\s+-[rfRF]{1,4}\b",
        r"\bmkfs\b",
        r"\bdd\s+if=",
        r"\b:\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",
        r"\bsystemctl\s+(stop|restart|disable)\s+(systemd|sshd|networking)\b",
        r"\bchmod\s+-[R]\s+777\s+/\b",
        r"\bshutdown\b",
        r"\breboot\b",
        r"\bDROP\s+DATABASE\b",
        r"\bTRUNCATE\s+TABLE\s+users\b",
        r">+\s*/dev/sda\b"
    ]

    SECRET_PATTERNS = [
        r"ghp_[a-zA-Z0-9]{36}",
        r"github_pat_[a-zA-Z0-9_]{82}",
        r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}",
        r"AIza[0-9A-Za-z-_]{35}",
        r"sk-[a-zA-Z0-9]{48}",
        r"0x[a-fA-F0-9]{64}"
    ]

    PROTECTED_INFRASTRUCTURE = [
        "169.254.169.254",
        "metadata.google.internal",
        "0.0.0.0"
    ]

    def __init__(self):
        self._destructive = [re.compile(p, re.IGNORECASE) for p in self.DESTRUCTIVE_PATTERNS]
        self._secrets = [re.compile(p) for p in self.SECRET_PATTERNS]

    def inspect_instruction(self, text: str) -> Tuple[bool, Optional[str]]:
        """Scans string for destructive commands."""
        for pattern in self._destructive:
            if pattern.search(text):
                logger.critical(f"BLOCKED DESTRUCTIVE INSTRUCTION: {text[:100]}")
                return False, f"Instruction rejected: Matched destructive pattern '{pattern.pattern}'."
        return True, None

    def sanitize_secrets(self, text: str) -> str:
        """Redacts sensitive credentials from output."""
        sanitized = text
        for pattern in self._secrets:
            sanitized = pattern.sub("[EKHTIZALY_PROTECTED_CREDENTIAL]", sanitized)
        return sanitized

    def check_execution(self, server: str, tool: str, arguments: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Pre-execution validation for tool invocations."""
        arg_str = str(arguments)
        valid, err = self.inspect_instruction(arg_str)
        if not valid:
            return False, err
            
        if "url" in arguments:
            url_lower = str(arguments["url"]).lower()
            for protected in self.PROTECTED_INFRASTRUCTURE:
                if protected in url_lower:
                    return False, f"Target '{protected}' is blocked by security policy."
                    
        if server in ["database", "memory"] and "sql" in arguments:
            q = str(arguments["sql"]).strip().upper()
            if q.startswith("DROP") or q.startswith("ALTER") or "TRUNCATE" in q:
                return False, "Schema modification commands are restricted."

        return True, None

    check_tool_execution = check_execution

security_guard = EkhtizalySecurityGuard()
sandbox_guard = security_guard
