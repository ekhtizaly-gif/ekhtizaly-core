import time
import random
import asyncio
from typing import Dict, Any, Optional

class EkhtizalyStealthLimiter:
    """
    Ekhtizaly Core Adaptive Stealth & Token-Bucket Rate Limiter.
    Emulates natural human browsing intervals and rotates browser headers.
    """
    
    ROTATING_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
    ]

    def __init__(self, target_rate_per_sec: float = 3.0, capacity: int = 5):
        self.rate = target_rate_per_sec
        self.capacity = capacity
        self.tokens = capacity
        self.last_timestamp = time.time()
        self._lock = asyncio.Lock()

    async def throttle(self):
        """Applies human micro-jitter and enforces rate capacity."""
        async with self._lock:
            current = time.time()
            delta = current - self.last_timestamp
            self.last_timestamp = current
            self.tokens = min(self.capacity, self.tokens + delta * self.rate)
            
            if self.tokens < 1.0:
                wait_time = (1.0 - self.tokens) / self.rate + random.uniform(0.05, 0.15)
                await asyncio.sleep(wait_time)
                self.tokens = 0.0
            else:
                self.tokens -= 1.0
                await asyncio.sleep(random.uniform(0.02, 0.05))

    def enforce_rate_limit(self, target: Optional[str] = None):
        """Synchronous light jitter for outbound requests."""
        time.sleep(random.uniform(0.03, 0.08))

    def get_headers(self) -> Dict[str, str]:
        """Returns realistic stealth request headers."""
        return {
            "User-Agent": random.choice(self.ROTATING_USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "DNT": "1",
            "Sec-Ch-Ua": '"Chromium";v="125", "Google Chrome";v="125"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }

stealth_limiter = EkhtizalyStealthLimiter()
