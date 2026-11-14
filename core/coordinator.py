import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional
from mcp_servers.router import router
from memory.semantic_vault import vault
from memory.session_store import session_store
from core.event_stream import event_stream

class EkhtizalyCoordinator:
    """
    Ekhtizaly Autonomous Core - Multi-Agent Swarm Orchestrator.
    Manages end-to-end autonomous missions, dispatches specialized agents,
    coordinates MCP tool pipelines, and ensures persistent state indexing.
    """

    def __init__(self):
        self.router = router
        self.vault = vault
        self.session_store = session_store

    async def run_mission(self, title: str, instructions: List[Dict[str, Any]], session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes a sequence of autonomous actions across MCP servers,
        logging telemetry, broadcasting real-time events, and storing results.
        """
        mission_id = f"mis_{uuid.uuid4().hex[:10]}"
        self.vault.record_mission_start(mission_id=mission_id, title=title, params={"instructions": instructions})
        
        await event_stream.broadcast(
            event_type="mission_started",
            payload={"mission_id": mission_id, "title": title, "steps_count": len(instructions)}
        )

        execution_steps = []
        overall_status = "SUCCESS"

        for idx, step in enumerate(instructions):
            server = step.get("server")
            tool = step.get("tool")
            args = step.get("arguments", {})
            desc = step.get("description", f"Step {idx+1}")

            await event_stream.broadcast(
                event_type="step_started",
                payload={"mission_id": mission_id, "step_index": idx, "description": desc, "tool": tool}
            )

            res = await self.router.execute_tool(server_key=server, tool_name=tool, arguments=args)
            
            step_record = {
                "step_index": idx,
                "description": desc,
                "server": server,
                "tool": tool,
                "arguments": args,
                "result": res,
                "status": res.get("status", "UNKNOWN")
            }
            execution_steps.append(step_record)

            await event_stream.broadcast(
                event_type="step_completed",
                payload={"mission_id": mission_id, "step_index": idx, "status": res.get("status")}
            )

            if res.get("status") in ["ERROR", "BLOCKED_BY_SECURITY_GUARD"]:
                overall_status = "PARTIAL_SUCCESS" if idx > 0 else "FAILED"

        final_result = {
            "mission_id": mission_id,
            "title": title,
            "status": overall_status,
            "total_steps": len(instructions),
            "completed_steps": len(execution_steps),
            "steps": execution_steps
        }

        self.vault.record_mission_completion(
            mission_id=mission_id,
            status=overall_status,
            steps=execution_steps,
            result=final_result
        )

        if session_id:
            self.session_store.add_message(
                session_id=session_id,
                role="assistant",
                content=f"Mission '{title}' completed with status: {overall_status}",
                tool_calls=[{"mission_id": mission_id, "status": overall_status}]
            )

        await event_stream.broadcast(
            event_type="mission_finished",
            payload={"mission_id": mission_id, "status": overall_status}
        )

        return final_result

coordinator = EkhtizalyCoordinator()
