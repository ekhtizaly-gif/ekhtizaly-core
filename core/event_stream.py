import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Any, List

class EkhtizalyEventStream:
    """
    Ekhtizaly Autonomous Core - Real-Time Server-Sent Events (SSE) Bus.
    Streams execution steps, telemetry, and live agent reasoning to connected frontends.
    """

    def __init__(self):
        self._subscribers: List[asyncio.Queue] = []

    async def subscribe(self) -> AsyncGenerator[str, None]:
        queue = asyncio.Queue(maxsize=100)
        self._subscribers.append(queue)
        try:
            # Yield initial connection heartbeat
            initial_event = {
                "event": "connected",
                "timestamp": time.time(),
                "message": "Ekhtizaly Real-Time Event Stream Connected"
            }
            yield f"data: {json.dumps(initial_event)}\n\n"

            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if queue in self._subscribers:
                self._subscribers.remove(queue)

    async def broadcast(self, event_type: str, payload: Dict[str, Any]):
        """Dispatches an event payload to all active web listeners."""
        event_data = {
            "event": event_type,
            "timestamp": time.time(),
            "payload": payload
        }
        for q in list(self._subscribers):
            try:
                if not q.full():
                    await q.put(event_data)
            except Exception:
                pass

event_stream = EkhtizalyEventStream()
