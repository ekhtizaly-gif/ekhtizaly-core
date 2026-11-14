import urllib.request
import urllib.parse
import json
import time
from typing import Dict, Any, List, Optional
import itertools

class EkhtizalyIntelligenceRadar:
    """
    Ekhtizaly Autonomous Core - Developer Community & Market Intelligence Radar.
    Monitors GitHub trends, discussions, community demand, and open-source ecosystems
    with automatic token rotation and rate-limit resilience.
    """

    def __init__(self):
        self.tokens: List[str] = []
        try:
            import os
            env_tokens = os.getenv("GITHUB_TOKENS", "").strip()
            if env_tokens:
                self.tokens = [t.strip() for t in env_tokens.split(",") if t.strip()]
            else:
                import sys
                from pathlib import Path
                home_token_file = Path.home() / "github_tokens.py"
                if home_token_file.exists():
                    sys.path.append(str(Path.home()))
                    from github_tokens import GITHUB_TOKENS
                    self.tokens = [t.strip() for t in GITHUB_TOKENS if t.strip()]
        except Exception:
            self.tokens = []

        self._token_cycle = itertools.cycle(self.tokens) if self.tokens else None

    def _get_token(self) -> Optional[str]:
        if self._token_cycle:
            return next(self._token_cycle)
        return None

    def search_github_repositories(self, query: str, sort: str = "stars", limit: int = 10) -> Dict[str, Any]:
        """Searches GitHub repositories by query and stars/forks/updated."""
        sanitized_query = query.strip()
        encoded_query = urllib.parse.quote(sanitized_query)
        url = f"https://api.github.com/search/repositories?q={encoded_query}&sort={sort}&order=desc&per_page={limit}"

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Ekhtizaly-Autonomous-Radar/2.0"
        }
        token = self._get_token()
        if token:
            headers["Authorization"] = f"token {token}"

        req = urllib.request.Request(url, headers=headers)
        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode())
                items = data.get("items", [])
                parsed = []
                for item in items:
                    parsed.append({
                        "name": item.get("full_name"),
                        "stars": item.get("stargazers_count"),
                        "forks": item.get("forks_count"),
                        "description": item.get("description"),
                        "url": item.get("html_url"),
                        "language": item.get("language"),
                        "topics": item.get("topics", []),
                        "open_issues": item.get("open_issues_count"),
                        "license": (item.get("license") or {}).get("name")
                    })
                return {
                    "status": "SUCCESS",
                    "total_count": data.get("total_count", 0),
                    "returned": len(parsed),
                    "items": parsed,
                    "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
            }

    def search_discussions_and_issues(self, repo: str, query: str, limit: int = 10) -> Dict[str, Any]:
        """Searches issues and discussions within a target repository."""
        full_query = f"repo:{repo} {query}".strip()
        encoded_query = urllib.parse.quote(full_query)
        url = f"https://api.github.com/search/issues?q={encoded_query}&sort=comments&order=desc&per_page={limit}"

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Ekhtizaly-Autonomous-Radar/2.0"
        }
        token = self._get_token()
        if token:
            headers["Authorization"] = f"token {token}"

        req = urllib.request.Request(url, headers=headers)
        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode())
                items = data.get("items", [])
                parsed = []
                for item in items:
                    parsed.append({
                        "title": item.get("title"),
                        "state": item.get("state"),
                        "comments_count": item.get("comments"),
                        "author": (item.get("user") or {}).get("login"),
                        "url": item.get("html_url"),
                        "created_at": item.get("created_at"),
                        "body_snippet": (item.get("body") or "")[:200]
                    })
                return {
                    "status": "SUCCESS",
                    "total_matches": data.get("total_count", 0),
                    "items": parsed,
                    "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
            }

intelligence_radar = EkhtizalyIntelligenceRadar()
