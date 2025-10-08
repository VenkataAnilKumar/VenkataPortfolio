from .llm_adapter import LLMAdapter
from ..telemetry.audit import audit_step
import time


@audit_step("recommendation")
async def run_recommendation(classification: dict, enrichment: dict):
    adapter = LLMAdapter()
    start = time.perf_counter()
    result = await adapter.recommend(classification, enrichment)
    result["latency_ms"] = int((time.perf_counter() - start) * 1000)
    return result
