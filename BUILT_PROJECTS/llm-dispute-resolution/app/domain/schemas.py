from pydantic import BaseModel, Field, constr
from typing import Optional, List, Dict, Any
import time


Identifier = constr(strip_whitespace=True, min_length=1)


class DisputeIn(BaseModel):
    external_ref: Optional[str] = None
    customer_id: Optional[str] = None
    merchant_id: Optional[str] = None
    amount: int = Field(gt=0)
    currency: constr(min_length=3, max_length=3)
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


def utc_ms() -> int:
    return int(time.time() * 1000)
