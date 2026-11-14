import asyncio
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from config.settings import PLATFORM_NAME, PLATFORM_CODE, PLATFORM_VERSION, ORGANIZATION, GATEWAY_PORT
from mcp_servers.router import router
from core.coordinator import coordinator
from core.event_stream import event_stream
from memory.semantic_vault import vault
from memory.session_store import session_store
from observability.telemetry import telemetry

from workflows.lead_discovery import lead_discovery
from workflows.price_sentinel import price_sentinel
from workflows.contract_auditor import contract_auditor

app = FastAPI(
    title=PLATFORM_NAME,
    version=PLATFORM_VERSION,
    description="Proprietary Autonomous Multi-Agent & Universal Tool Integration Gateway."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ToolExecuteRequest(BaseModel):
    server: str
    tool: str
    arguments: Optional[Dict[str, Any]] = {}

class MissionRequest(BaseModel):
    title: str
    instructions: List[Dict[str, Any]]
    session_id: Optional[str] = None

class LeadHunterRequest(BaseModel):
    keyword: Optional[str] = "mcp servers ai"
    limit: Optional[int] = 5

class PriceSentinelRequest(BaseModel):
    url: str
    item_name: str
    threshold_price: Optional[float] = None

class ContractAuditRequest(BaseModel):
    contract_address: str

@app.get("/")
async def root():
    return {
        "platform": PLATFORM_NAME,
        "code": PLATFORM_CODE,
        "version": PLATFORM_VERSION,
        "organization": ORGANIZATION,
        "status": "ONLINE",
        "docs_url": "/docs"
    }

@app.get("/api/status")
async def get_system_status():
    tools = await router.get_tool_catalog()
    metrics = telemetry.get_metrics_summary()
    return {
        "platform": PLATFORM_NAME,
        "status": "HEALTHY",
        "timestamp": time.time(),
        "total_tools_registered": len(tools),
        "active_mcp_servers": list(router.servers.keys()),
        "telemetry_metrics": metrics
    }

@app.get("/api/tools")
async def list_tools():
    catalog = await router.get_tool_catalog()
    return {
        "count": len(catalog),
        "tools": catalog
    }

@app.post("/api/execute")
async def execute_tool(req: ToolExecuteRequest):
    result = await router.execute_tool(
        server_key=req.server,
        tool_name=req.tool,
        arguments=req.arguments or {}
    )
    return result

@app.post("/api/mission")
async def create_mission(req: MissionRequest):
    result = await coordinator.run_mission(
        title=req.title,
        instructions=req.instructions,
        session_id=req.session_id
    )
    return result

@app.get("/api/missions/{mission_id}")
async def get_mission(mission_id: str):
    res = vault.get_mission(mission_id)
    if not res:
        raise HTTPException(status_code=404, detail="Mission not found in vault")
    return res

@app.get("/api/stream")
async def stream_events():
    return StreamingResponse(
        event_stream.subscribe(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/workflows/lead-hunter")
async def trigger_lead_hunter(req: LeadHunterRequest):
    res = await lead_discovery.execute(keyword=req.keyword or "mcp servers ai", limit=req.limit or 5)
    return res

@app.post("/api/workflows/price-sentinel")
async def trigger_price_sentinel(req: PriceSentinelRequest):
    res = await price_sentinel.execute(target_url=req.url, item_name=req.item_name, threshold_price=req.threshold_price)
    return res

@app.post("/api/workflows/contract-auditor")
async def trigger_contract_auditor(req: ContractAuditRequest):
    res = await contract_auditor.execute(contract_address=req.contract_address)
    return res

@app.get("/api/memory/search")
async def search_memory(q: str = Query(..., min_length=2), limit: int = 5):
    results = vault.search_documents(query=q, limit=limit)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }

@app.get("/api/memory/leads")
async def get_harvested_leads(source: Optional[str] = None, limit: int = 20):
    leads = vault.list_leads(source=source, limit=limit)
    return {
        "count": len(leads),
        "leads": leads
    }

@app.get("/api/telemetry")
async def get_telemetry():
    return telemetry.get_metrics_summary()
