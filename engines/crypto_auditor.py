import urllib.request
import json
import time
from typing import Dict, Any, Optional
from config.settings import DEFAULT_EVM_RPC, EVM_WALLET

class EkhtizalyCryptoAuditor:
    """
    Ekhtizaly Autonomous Core - Web3 & EVM Autonomous Auditor.
    Direct JSON-RPC interface to audit smart contracts, monitor EVM balances,
    and estimate gas across Base L2, Ethereum, and Arbitrum.
    """

    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or DEFAULT_EVM_RPC

    def _call_rpc(self, method: str, params: list) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": int(time.time() * 1000)
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        req = urllib.request.Request(self.rpc_url, data=data, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())

    def get_wallet_balance(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """Fetches the native ETH/token balance for the target wallet address."""
        target_wallet = wallet_address or EVM_WALLET
        start_time = time.time()
        try:
            res = self._call_rpc("eth_getBalance", [target_wallet, "latest"])
            if "result" in res:
                wei_val = int(res["result"], 16)
                eth_val = wei_val / 1e18
                return {
                    "status": "SUCCESS",
                    "wallet": target_wallet,
                    "balance_wei": str(wei_val),
                    "balance_eth": round(eth_val, 6),
                    "rpc": self.rpc_url,
                    "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
                }
            return {"status": "ERROR", "error": res.get("error", "Unknown RPC error")}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def get_gas_price(self) -> Dict[str, Any]:
        """Fetches current network gas price in Gwei."""
        start_time = time.time()
        try:
            res = self._call_rpc("eth_gasPrice", [])
            if "result" in res:
                wei_val = int(res["result"], 16)
                gwei_val = wei_val / 1e9
                return {
                    "status": "SUCCESS",
                    "gas_price_wei": str(wei_val),
                    "gas_price_gwei": round(gwei_val, 4),
                    "rpc": self.rpc_url,
                    "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
                }
            return {"status": "ERROR", "error": res.get("error", "Failed to fetch gas price")}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def verify_contract_code(self, contract_address: str) -> Dict[str, Any]:
        """Verifies if an address is an active smart contract and checks bytecode length."""
        start_time = time.time()
        try:
            res = self._call_rpc("eth_getCode", [contract_address, "latest"])
            code = res.get("result", "0x")
            is_contract = len(code) > 2
            return {
                "status": "SUCCESS",
                "contract_address": contract_address,
                "is_smart_contract": is_contract,
                "bytecode_bytes": (len(code) - 2) // 2 if is_contract else 0,
                "elapsed_ms": round((time.time() - start_time) * 1000.0, 2)
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

crypto_auditor = EkhtizalyCryptoAuditor()
