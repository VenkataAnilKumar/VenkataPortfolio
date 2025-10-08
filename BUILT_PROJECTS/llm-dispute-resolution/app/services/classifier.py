from .llm_adapter import LLMAdapter
from ..telemetry.audit import audit_step
import time


@audit_step("classification")
async def run_classification(narrative: str, amount_cents: int, currency: str):
    adapter = LLMAdapter()
    start = time.perf_counter()
    result = await adapter.classify(narrative, amount_cents, currency)
    latency = int((time.perf_counter() - start) * 1000)
    result["latency_ms"] = latency
    return result
