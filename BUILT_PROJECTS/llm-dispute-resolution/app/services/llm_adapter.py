from ..core.config import get_settings


class LLMAdapter:
    def __init__(self):
        self.settings = get_settings()


    async def classify(self, narrative: str, amount_cents: int, currency: str):
        if self.settings.mock_llm:
            narrative_lower = narrative.lower()
            prompt_tokens = min(100 + len(narrative) // 20, 500)
            completion_tokens = 30
            total_tokens = prompt_tokens + completion_tokens
            cost = round(total_tokens / 1000 * 0.002, 6)
            # Expanded taxonomy with more types
            taxonomy = [
                ("FRAUD_UNAUTHORIZED", ["not authorize", "did not", "unauthorized", "unknown charge"]),
                ("MERCHANT_ERROR", ["merchant error", "wrong item", "overcharged", "incorrect amount", "double charged", "billed twice"]),
                ("SERVICE_NOT_RECEIVED", ["not received", "never arrived", "missing item", "didn't get", "no delivery", "never shipped"]),
                ("FRAUD_CARD_LOST", ["lost card", "stolen card", "card stolen", "card lost"]),
                ("FRAUD_ACCOUNT_TAKEOVER", ["account hacked", "account takeover", "unauthorized login"]),
                ("FRIENDLY_FRAUD_RISK", ["family", "friend", "child", "accidentally", "mistake", "my kid"]),
                ("SUBSCRIPTION_CANCELLATION", ["cancel subscription", "didn't cancel", "charged after cancel", "subscription issue"]),
                ("REFUND_NOT_PROCESSED", ["refund not received", "refund missing", "refund issue"]),
            ]
            for label, keywords in taxonomy:
                if any(kw in narrative_lower for kw in keywords):
                    confidence = 0.9 if label.startswith("FRAUD") else 0.85
                    return {
                        "label": label,
                        "confidence": confidence,
                        "rationale": f"Pattern matches {label.replace('_', ' ').title()} keywords",
                        "token_usage": total_tokens,
                        "cost_usd": cost
                    }
            # Fallback: rules-based if no match
            fallback = {
                "label": "OTHER",
                "confidence": 0.7,
                "rationale": "No strong fraud, error, or service keywords detected (fallback)",
                "token_usage": total_tokens,
                "cost_usd": cost
            }
            return fallback
        # If not mock, add try/except for real LLM call and fallback
        raise NotImplementedError("Real LLM integration not implemented in portfolio mode")

    async def recommend(self, classification: dict, enrichment: dict):
        if self.settings.mock_llm:
            prompt_tokens = 80
            completion_tokens = 40
            total_tokens = prompt_tokens + completion_tokens
            cost = round(total_tokens / 1000 * 0.004, 6)
            label = classification.get("label")
            confidence = classification.get("confidence", 0)
            prior_disputes = enrichment.get("prior_disputes", 0)
            recent_transactions = enrichment.get("recent_transactions", 0)

            # More nuanced recommendation logic
            if label == "FRAUD_UNAUTHORIZED" and confidence > 0.8:
                action = "REFUND"
                rationale = "High confidence unauthorized fraud pattern."
                rec_conf = 0.81
            elif label == "MERCHANT_ERROR" and confidence > 0.8:
                action = "REQUEST_INFO"
                rationale = "Merchant error detected; request more info from merchant."
                rec_conf = 0.78
            elif label == "SERVICE_NOT_RECEIVED" and prior_disputes == 0:
                action = "REFUND"
                rationale = "No prior disputes; likely valid claim for non-receipt."
                rec_conf = 0.77
            elif label == "FRIENDLY_FRAUD_RISK" or prior_disputes > 2:
                action = "ESCALATE_REVIEW"
                rationale = "Potential friendly fraud or repeat disputes; escalate for manual review."
                rec_conf = 0.7
            elif label == "SUBSCRIPTION_CANCELLATION":
                action = "REQUEST_INFO"
                rationale = "Subscription cancellation issue; request supporting documentation."
                rec_conf = 0.75
            elif label == "REFUND_NOT_PROCESSED":
                action = "ESCALATE_REVIEW"
                rationale = "Refund not processed; escalate for finance team review."
                rec_conf = 0.72
            else:
                action = "ESCALATE_REVIEW"
                rationale = "Insufficient confidence or unclear pattern; escalate for analyst review."
                rec_conf = 0.65

            return {
                "action": action,
                "confidence": rec_conf,
                "rationale": rationale,
                "token_usage": total_tokens,
                "cost_usd": cost
            }
        raise NotImplementedError
