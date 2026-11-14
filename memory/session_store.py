import time
import uuid
from typing import Dict, Any, List, Optional

class EkhtizalySessionStore:
    """
    Ekhtizaly Autonomous Core - Session and Active Dialogue State Manager.
    Maintains in-memory short-term context while synchronizing state checkpoints.
    """

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, title: str = "Active Session", metadata: Optional[Dict[str, Any]] = None) -> str:
        session_id = f"ses_{uuid.uuid4().hex[:12]}"
        self._sessions[session_id] = {
            "session_id": session_id,
            "title": title,
            "created_at": time.time(),
            "updated_at": time.time(),
            "metadata": metadata or {},
            "history": []
        }
        return session_id

    def add_message(self, session_id: str, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None) -> bool:
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "session_id": session_id,
                "title": "Restored Session",
                "created_at": time.time(),
                "updated_at": time.time(),
                "metadata": {},
                "history": []
            }
        
        entry = {
            "role": role,
            "content": content,
            "tool_calls": tool_calls or [],
            "timestamp": time.time()
        }
        self._sessions[session_id]["history"].append(entry)
        self._sessions[session_id]["updated_at"] = time.time()
        return True

    def get_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        if session_id not in self._sessions:
            return []
        return self._sessions[session_id]["history"][-limit:]

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        return [
            {
                "session_id": s["session_id"],
                "title": s["title"],
                "created_at": s["created_at"],
                "updated_at": s["updated_at"],
                "message_count": len(s["history"])
            }
            for s in self._sessions.values()
        ]

session_store = EkhtizalySessionStore()
