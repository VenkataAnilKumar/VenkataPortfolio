from ..llm.adapter import llm_adapter
from ..telemetry.audit import audit_step
import time


@audit_step("classification")
async def run_classification(narrative: str, amount_cents: int, currency: str):
    """
    Classify a dispute using the advanced LLM adapter
    
    Args:
        narrative: Customer dispute description
        amount_cents: Transaction amount in cents
        currency: Transaction currency code
        
    Returns:
        Dict containing classification results with enhanced metadata
    """
    start = time.perf_counter()
    
    try:
        result = await llm_adapter.classify_dispute(narrative, amount_cents, currency)
        latency = int((time.perf_counter() - start) * 1000)
        result["latency_ms"] = latency
        return result
    except Exception as e:
        # Enhanced error handling with fallback
        latency = int((time.perf_counter() - start) * 1000)
        return {
            "label": "OTHER",
            "confidence": 0.5,
            "rationale": f"Classification failed: {str(e)}",
            "latency_ms": latency,
            "cost_usd": 0.0,
            "token_usage": 0,
            "model_used": "fallback",
            "error": True
        }
