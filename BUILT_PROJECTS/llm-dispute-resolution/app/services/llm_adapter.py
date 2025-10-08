from ..core.config import get_settings


class LLMAdapter:
    def __init__(self):
        self.settings = get_settings()


    async def classify(self, narrative: str, amount_cents: int, currency: str):
        if self.settings.mock_llm:
            narrative_lower = narrative.lower()
            # Expanded taxonomy
            if any(kw in narrative_lower for kw in ["not authorize", "did not", "unauthorized", "unknown charge"]):
                return {
                    "label": "FRAUD_UNAUTHORIZED",
                    "confidence": 0.91,
                    "rationale": "Pattern matches unauthorized/fraud claim phrases"
                }
            if any(kw in narrative_lower for kw in ["merchant error", "wrong item", "overcharged", "incorrect amount"]):
                return {
                    "label": "MERCHANT_ERROR",
                    "confidence": 0.87,
                    "rationale": "Merchant error or billing issue detected"
                }
            if any(kw in narrative_lower for kw in ["not received", "never arrived", "missing item", "didn't get"]):
                return {
                    "label": "SERVICE_NOT_RECEIVED",
                    "confidence": 0.85,
                    "rationale": "Service or product not received keywords detected"
                }
            if any(kw in narrative_lower for kw in ["family", "friend", "child", "accidentally", "mistake"]):
                return {
                    "label": "FRIENDLY_FRAUD_RISK",
                    "confidence": 0.80,
                    "rationale": "Possible friendly fraud or accidental use"
                }
            return {"label": "OTHER", "confidence": 0.72, "rationale": "No strong fraud or error keywords detected"}
        raise NotImplementedError("Real LLM integration not implemented in portfolio mode")

    async def recommend(self, classification: dict, enrichment: dict):
        if self.settings.mock_llm:
            label = classification.get("label")
            if label == "FRAUD_UNAUTHORIZED" and classification.get("confidence", 0) > 0.8:
                return {
                    "action": "REFUND",
                    "confidence": 0.81,
                    "rationale": "High confidence unauthorized fraud pattern"
                }
            return {
                "action": "ESCALATE_REVIEW",
                "confidence": 0.65,
                "rationale": "Insufficient confidence for automated resolution"
            }
        raise NotImplementedError
