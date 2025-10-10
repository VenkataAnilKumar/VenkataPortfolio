from ..telemetry.audit import audit_step
import time


# For MVP we mock enrichment; in a real system we'd query transactions & prior disputes.

@audit_step("enrichment")
async def run_enrichment(dispute_id: str):
    start = time.perf_counter()
    # Simulated enrichment
    enrichment = {
        "recent_transactions": 5,
        "prior_disputes": 2
    }
    enrichment["latency_ms"] = int((time.perf_counter() - start) * 1000)
    return enrichment
