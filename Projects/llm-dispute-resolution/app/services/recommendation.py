from ..llm.adapter import llm_adapter
from ..telemetry.audit import audit_step
import time


@audit_step("recommendation")
async def run_recommendation(classification: dict, enrichment: dict):
    """
    Generate action recommendation using the advanced LLM adapter
    
    Args:
        classification: Results from classification step
        enrichment: Results from enrichment step
        
    Returns:
        Dict containing recommendation with enhanced metadata
    """
    start = time.perf_counter()
    
    try:
        result = await llm_adapter.recommend_action(classification, enrichment)
        latency = int((time.perf_counter() - start) * 1000)
        result["latency_ms"] = latency
        return result
    except Exception as e:
        # Enhanced error handling with fallback
        latency = int((time.perf_counter() - start) * 1000)
        return {
            "action": "ESCALATE_REVIEW",
            "confidence": 0.5,
            "rationale": f"Recommendation failed, escalating for manual review: {str(e)}",
            "latency_ms": latency,
            "cost_usd": 0.0,
            "token_usage": 0,
            "model_used": "fallback",
            "error": True
        }
