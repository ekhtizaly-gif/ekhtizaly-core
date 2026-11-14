import asyncio
import sys
import time
from pathlib import Path

# Set up module path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import PLATFORM_NAME, PLATFORM_VERSION
from security.sandbox_guard import sandbox_guard
from memory.semantic_vault import vault
from memory.session_store import session_store
from observability.telemetry import telemetry
from mcp_servers.router import router
from core.coordinator import coordinator
from workflows.lead_discovery import lead_discovery
from workflows.contract_auditor import contract_auditor

async def run_tests():
    print("=" * 70)
    print(f"🚀 [EKHTIZALY AUTONOMOUS CORE v{PLATFORM_VERSION}] - AUTOMATED FULL TEST HARNESS")
    print(f"Platform: {PLATFORM_NAME}")
    print("=" * 70)

    passed = 0
    total = 0

    def assert_test(name: str, condition: bool, extra: str = ""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✅ PASS: {name} {extra}")
        else:
            print(f"  ❌ FAIL: {name} {extra}")

    # TEST 1: Security Sandbox Guard
    print("\n[Phase 1] Security Sandbox Firewall Verification")
    blocked, err = sandbox_guard.inspect_instruction("rm -rf /")
    assert_test("Destructive command block ('rm -rf /')", not blocked, f"(Reason: {err})")

    allowed, err = sandbox_guard.inspect_instruction("echo 'safe operations'")
    assert_test("Safe instruction allowed", allowed)

    sec_url, sec_err = sandbox_guard.check_execution("web", "extract_clean_markdown", {"url": "http://169.254.169.254/latest/meta-data"})
    assert_test("Cloud Metadata URL SSRF block", not sec_url, f"(Blocked: {sec_err})")

    # TEST 2: Memory & Semantic FTS5 Vault
    print("\n[Phase 2] Semantic Knowledge Vault (SQLite + FTS5 BM25)")
    doc_id = "test_doc_001"
    vault.store_document(
        doc_id=doc_id,
        title="Autonomous AI Agent Protocols",
        content="Model Context Protocol (MCP) connects AI models to external tools and enterprise data pipelines.",
        category="protocols"
    )
    search_results = vault.search_documents("Protocol external tools", limit=3)
    found = any(r["doc_id"] == doc_id for r in search_results)
    assert_test("FTS5 BM25 Search & Document Retrieval", found, f"(Found {len(search_results)} matches)")

    # TEST 3: Telemetry & Tracing
    print("\n[Phase 3] Enterprise Observability & Telemetry")
    t_id = telemetry.start_trace("TestEngine", "TestOp")
    time.sleep(0.01)
    latency = telemetry.end_trace(t_id, status="SUCCESS")
    summary = telemetry.get_metrics_summary()
    assert_test("Trace lifecycle and latency calculation", latency > 0 and "TestEngine::TestOp" in summary["operations"])

    # TEST 4: Tool Catalog Verification
    print("\n[Phase 4] MCP Servers & 20-Tool Catalog Discovery")
    tools = await router.get_tool_catalog()
    assert_test("Tool Catalog Discovery (Expect exactly 20 tools)", len(tools) == 20, f"(Discovered: {len(tools)} tools)")

    expected_servers = {"web", "browser", "intelligence", "automation", "crypto", "memory"}
    discovered_servers = set(t["server"] for t in tools)
    assert_test("All 6 specialized MCP servers present", expected_servers == discovered_servers, f"({discovered_servers})")

    # TEST 5: Live Tool Invocations
    print("\n[Phase 5] Live Tool Execution via Unified Router")
    # A. Crypto Tool (Base L2 RPC)
    crypto_res = await router.execute_tool("crypto", "get_network_gas_price", {})
    assert_test(
        "Crypto Tool (Base L2 Gas Price RPC)",
        crypto_res.get("status") == "SUCCESS" and "gas_price_gwei" in crypto_res.get("result", {}),
        f"(Gas: {crypto_res.get('result', {}).get('gas_price_gwei')} Gwei)"
    )

    # B. Memory Tool
    mem_res = await router.execute_tool("memory", "vault_search_knowledge", {"query": "protocols", "limit": 2})
    assert_test(
        "Memory Tool (Vault Search MCP)",
        mem_res.get("status") == "SUCCESS",
        f"(Matches: {mem_res.get('result', {}).get('matches_count')})"
    )

    # C. Intelligence Tool (Momentum Analysis)
    intel_res = await router.execute_tool("intelligence", "analyze_topic_momentum", {"topic": "crawl4ai"})
    assert_test(
        "Intelligence Tool (Topic Momentum Analysis)",
        intel_res.get("status") == "SUCCESS",
        f"(Top: {intel_res.get('result', {}).get('top_repositories')})"
    )

    # TEST 6: Autonomous Workflows
    print("\n[Phase 6] Autonomous End-to-End Workflows")
    # A. Contract Auditor Workflow
    audit_res = await contract_auditor.execute("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913") # USDC on Base
    assert_test(
        "Smart Contract Security Auditor Workflow (USDC Base)",
        audit_res.get("status") == "SUCCESS" and audit_res.get("audit_report", {}).get("is_contract") == True,
        f"(Bytecode size: {audit_res.get('audit_report', {}).get('bytecode_size')} bytes, Safety: {audit_res.get('audit_report', {}).get('safety_score')}/100)"
    )

    # B. Lead Discovery Workflow
    lead_res = await lead_discovery.execute(keyword="crawl4ai", limit=2)
    assert_test(
        "Lead Discovery Autonomous Workflow",
        lead_res.get("status") == "SUCCESS",
        f"(Discovered {lead_res.get('leads_discovered')} leads)"
    )

    # TEST 7: Multi-Agent Coordinator Mission
    print("\n[Phase 7] Multi-Agent Coordinator Swarm Mission")
    mission_instructions = [
        {
            "server": "crypto",
            "tool": "check_wallet_balance",
            "arguments": {"wallet_address": "0xb6A9c8c8085dF59A3329AdE5dCC2fD4A9Ca5212d"},
            "description": "Inspect Ekhtizaly Treasury Wallet Balance"
        },
        {
            "server": "memory",
            "tool": "vault_search_knowledge",
            "arguments": {"query": "AI Agent"},
            "description": "Query Internal Knowledge Base"
        }
    ]
    mission_res = await coordinator.run_mission("Operational Readiness Audit", mission_instructions)
    assert_test(
        "Coordinator Mission Execution & Vault State Logging",
        mission_res.get("status") == "SUCCESS" and mission_res.get("completed_steps") == 2,
        f"(Mission ID: {mission_res.get('mission_id')})"
    )

    print("\n" + "=" * 70)
    print(f"🏁 TEST RESULTS: {passed}/{total} PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 70)

    if passed == total:
        print("🎉 ALL SYSTEMS FULLY OPERATIONAL WITH 100% SUCCESS!")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
