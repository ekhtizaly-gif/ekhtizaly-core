import time
import asyncio
import json
from typing import Dict, Any, List, Optional
from mcp_servers.web_scraping_server import server as web_mcp
from mcp_servers.browser_agent_server import server as browser_mcp
from mcp_servers.intelligence_server import server as intel_mcp
from mcp_servers.automation_server import server as auto_mcp
from mcp_servers.crypto_audit_server import server as crypto_mcp
from mcp_servers.knowledge_memory_server import server as memory_mcp

from security.sandbox_guard import sandbox_guard
from observability.telemetry import telemetry
from core.event_stream import event_stream

SERVERS = {
    "web": web_mcp,
    "browser": browser_mcp,
    "intelligence": intel_mcp,
    "automation": auto_mcp,
    "crypto": crypto_mcp,
    "memory": memory_mcp
}

class EkhtizalyToolRouter:
    """
    Ekhtizaly Autonomous Core - Central MCP Tool Router.
    Aggregates the 6 specialized FastMCP servers, enforces security policies,
    records observability telemetry, and streams live execution events.
    """

    def __init__(self):
        self.servers = SERVERS

    async def get_tool_catalog(self) -> List[Dict[str, Any]]:
        """Returns full metadata for all 20 tools across all registered servers."""
        catalog = []
        for server_key, server_instance in self.servers.items():
            try:
                tools = await server_instance.list_tools() if asyncio.iscoroutinefunction(server_instance.list_tools) else server_instance.list_tools()
                for t in tools:
                    catalog.append({
                        "server": server_key,
                        "name": t.name,
                        "description": getattr(t, "description", "") or "",
                        "parameters": getattr(t, "parameters", {})
                    })
            except Exception:
                pass
        return catalog

    async def execute_tool(self, server_key: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validates security, invokes tool, and logs telemetry."""
        trace_id = telemetry.start_trace(component=f"MCP::{server_key}", operation=tool_name)
        
        # 1. Enforce Sandbox Boundary
        allowed, block_reason = sandbox_guard.check_tool_execution(server_key, tool_name, arguments)
        if not allowed:
            telemetry.end_trace(trace_id, status="BLOCKED", details={"reason": block_reason})
            return {
                "server": server_key,
                "tool": tool_name,
                "status": "BLOCKED_BY_SECURITY_GUARD",
                "reason": block_reason
            }

        server = self.servers.get(server_key.lower())
        if not server:
            telemetry.end_trace(trace_id, status="NOT_FOUND", details={"error": f"Server {server_key} missing"})
            return {"status": "ERROR", "error": f"MCP server '{server_key}' not found"}

        try:
            call_res = await server.call_tool(tool_name, arguments) if asyncio.iscoroutinefunction(server.call_tool) else server.call_tool(tool_name, arguments)
            
            # Unpack FastMCP response structures
            output = None
            if hasattr(call_res, "structured_content") and call_res.structured_content:
                output = call_res.structured_content
                if isinstance(output, dict) and "result" in output and len(output) == 1:
                    output = output["result"]
            elif hasattr(call_res, "content") and call_res.content:
                items = []
                for item in call_res.content:
                    if hasattr(item, "text"):
                        try:
                            items.append(json.loads(item.text))
                        except Exception:
                            items.append(item.text)
                    else:
                        items.append(str(item))
                output = items[0] if len(items) == 1 else items
            else:
                output = call_res

            elapsed_ms = telemetry.end_trace(trace_id, status="SUCCESS")

            # Broadcast SSE event
            await event_stream.broadcast(
                event_type="tool_execution",
                payload={
                    "server": server_key,
                    "tool": tool_name,
                    "arguments": arguments,
                    "latency_ms": elapsed_ms,
                    "status": "SUCCESS"
                }
            )

            return {
                "status": "SUCCESS",
                "server": server_key,
                "tool": tool_name,
                "latency_ms": elapsed_ms,
                "result": output
            }

        except Exception as e:
            elapsed_ms = telemetry.end_trace(trace_id, status="ERROR", details={"error": str(e)})
            return {
                "status": "ERROR",
                "server": server_key,
                "tool": tool_name,
                "error": str(e),
                "latency_ms": elapsed_ms
            }

router = EkhtizalyToolRouter()
