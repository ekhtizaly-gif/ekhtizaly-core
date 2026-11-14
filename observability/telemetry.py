import time
import uuid
from typing import Dict, Any, Optional
from memory.semantic_vault import vault

class EkhtizalyTelemetry:
    """
    Ekhtizaly Autonomous Core - Enterprise Observability & Telemetry Tracker.
    Records latency, operational status, trace spans, and error statistics.
    """

    def __init__(self):
        self.active_spans: Dict[str, Dict[str, Any]] = {}
        self.call_stats: Dict[str, Dict[str, Any]] = {}

    def start_trace(self, component: str, operation: str) -> str:
        trace_id = f"trace_{uuid.uuid4().hex[:12]}"
        self.active_spans[trace_id] = {
            "trace_id": trace_id,
            "component": component,
            "operation": operation,
            "start_time": time.time()
        }
        return trace_id

    def end_trace(self, trace_id: str, status: str = "SUCCESS", details: Optional[Dict[str, Any]] = None) -> float:
        span = self.active_spans.pop(trace_id, None)
        if not span:
            return 0.0

        latency_ms = (time.time() - span["start_time"]) * 1000.0
        component = span["component"]
        operation = span["operation"]

        # Update in-memory stats
        key = f"{component}::{operation}"
        if key not in self.call_stats:
            self.call_stats[key] = {
                "total_calls": 0,
                "errors": 0,
                "total_latency_ms": 0.0,
                "max_latency_ms": 0.0,
                "min_latency_ms": 999999.0
            }
        
        stat = self.call_stats[key]
        stat["total_calls"] += 1
        stat["total_latency_ms"] += latency_ms
        if status != "SUCCESS":
            stat["errors"] += 1
        if latency_ms > stat["max_latency_ms"]:
            stat["max_latency_ms"] = latency_ms
        if latency_ms < stat["min_latency_ms"]:
            stat["min_latency_ms"] = latency_ms

        # Persist to database
        try:
            vault.log_telemetry(
                trace_id=trace_id,
                component=component,
                operation=operation,
                status=status,
                latency_ms=round(latency_ms, 2),
                details=details
            )
        except Exception:
            pass

        return latency_ms

    def get_metrics_summary(self) -> Dict[str, Any]:
        summary = {}
        for key, stat in self.call_stats.items():
            calls = stat["total_calls"]
            avg_lat = stat["total_latency_ms"] / calls if calls > 0 else 0.0
            err_rate = (stat["errors"] / calls) * 100.0 if calls > 0 else 0.0
            summary[key] = {
                "total_calls": calls,
                "errors": stat["errors"],
                "error_rate_pct": round(err_rate, 2),
                "avg_latency_ms": round(avg_lat, 2),
                "max_latency_ms": round(stat["max_latency_ms"], 2),
                "min_latency_ms": round(stat["min_latency_ms"], 2) if calls > 0 else 0.0
            }
        return {
            "active_traces": len(self.active_spans),
            "operations": summary
        }

telemetry = EkhtizalyTelemetry()
