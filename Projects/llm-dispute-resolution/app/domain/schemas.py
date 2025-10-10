from pydantic import BaseModel, Field, constr
from typing import Optional, List, Dict, Any
import time


Identifier = constr(strip_whitespace=True, min_length=1)



# Stricter validation for input fields
class DisputeIn(BaseModel):
    external_ref: Optional[str] = Field(
        default=None, min_length=1, max_length=64, description="External reference ID (1-64 chars)"
    )
    customer_id: Optional[str] = Field(
        default=None, min_length=1, max_length=64, description="Customer ID (1-64 chars)"
    )
    merchant_id: Optional[str] = Field(
        default=None, min_length=1, max_length=64, description="Merchant ID (1-64 chars)"
    )
    amount: int = Field(gt=0)
    currency: str = Field(
        min_length=3, max_length=3, regex=r'^[A-Z]{3}$', description="ISO 4217 currency code (3 uppercase letters)"
    )
    narrative: str = Field(max_length=5000)


class Classification(BaseModel):
    label: str
    confidence: float
    rationale: str


class Recommendation(BaseModel):
    action: str
    confidence: float
    rationale: str


class DisputeOut(BaseModel):
    id: str
    external_ref: Optional[str]
    classification: Classification
    recommendation: Recommendation
    truncated: bool = False
    latency_ms: int


class MetricsOut(BaseModel):
    total_cases: int
    classification_latency_ms_p95: float
    recommendation_latency_ms_p95: float
    cases_by_label: Dict[str, int]
    avg_cost_per_case_usd: float


class AuditEventOut(BaseModel):
    step: str
    timestamp: float
    latency_ms: int
    success: bool
    details: Dict[str, Any] | None = None


class AuditLogOut(BaseModel):
    case_id: str
    events: List[AuditEventOut]


class EvidenceItemOut(BaseModel):
    id: str
    dispute_case_id: str
    source: str
    kind: str
    content: dict
    fetched_at: float
    agent_run_id: str | None = None


class TransactionLedgerOut(BaseModel):
    id: str
    customer_id: str
    merchant_id: str
    amount_cents: int
    currency: str
    occurred_at: float


def utc_ms() -> int:
    return int(time.time() * 1000)
