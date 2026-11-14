from fastmcp import FastMCP
from typing import Dict, Any
from engines.crypto_auditor import crypto_auditor

mcp = FastMCP("Ekhtizaly-Crypto-Audit-Server")

@mcp.tool()
async def check_wallet_balance(wallet_address: str) -> Dict[str, Any]:
    """Inspects native EVM balance and verification status for any target address."""
    return crypto_auditor.get_wallet_balance(wallet_address=wallet_address)

@mcp.tool()
async def get_network_gas_price() -> Dict[str, Any]:
    """Fetches real-time gas prices in Gwei across the Base L2 network."""
    return crypto_auditor.get_gas_price()

@mcp.tool()
async def verify_smart_contract(contract_address: str) -> Dict[str, Any]:
    """Inspects target address to determine if it contains deployed bytecode."""
    return crypto_auditor.verify_contract_code(contract_address=contract_address)

@mcp.tool()
async def audit_liquidity_pair(pair_address: str) -> Dict[str, Any]:
    """Audits contract validity and security readiness for a target DEX liquidity address."""
    code_res = crypto_auditor.verify_contract_code(contract_address=pair_address)
    bal_res = crypto_auditor.get_wallet_balance(wallet_address=pair_address)
    
    return {
        "status": "SUCCESS",
        "pair_address": pair_address,
        "is_contract": code_res.get("is_smart_contract", False),
        "bytecode_size": code_res.get("bytecode_bytes", 0),
        "contract_balance_eth": bal_res.get("balance_eth", 0.0),
        "audit_verdict": "ACTIVE_SMART_CONTRACT" if code_res.get("is_smart_contract") else "EMPTY_OR_EOA"
    }

server = mcp
