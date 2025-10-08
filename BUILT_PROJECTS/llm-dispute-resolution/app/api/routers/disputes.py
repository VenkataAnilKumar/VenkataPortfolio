
from fastapi import APIRouter, Depends, HTTPException, status
from ...domain.schemas import DisputeIn, DisputeOut, Classification, Recommendation, AuditLogOut, AuditEventOut
from ...core.config import get_settings
from ...services.orchestrator import process_case, get_dispute_by_id, get_audit_log
from ...domain.schemas import AuditLogOut, AuditEventOut
@router.get("/disputes/{dispute_id}/audit", response_model=AuditLogOut)
async def get_dispute_audit(dispute_id: str):
    events = await get_audit_log(dispute_id)
    if not events:
        raise HTTPException(status_code=404, detail="No audit events found for this dispute")
    audit_events = [
        AuditEventOut(
            step=e.step,
            timestamp=e.created_at.timestamp(),
            latency_ms=e.payload_json.get("latency_ms", 0),
            success=e.payload_json.get("success", True),
            details={k: v for k, v in e.payload_json.items() if k not in ("latency_ms", "success", "step", "timestamp")}
        ) for e in events
    ]
    return AuditLogOut(case_id=dispute_id, events=audit_events)
import uuid

router = APIRouter(tags=["disputes"])

def _auth(settings=Depends(get_settings), api_key: str | None = None):  # placeholder simple auth injection
    if settings.api_key:
        # In a fuller implementation we'd read header; simplified for brevity
        if api_key != settings.api_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UNAUTHORIZED")

@router.post("/disputes", response_model=DisputeOut, status_code=201)
async def create_dispute(payload: DisputeIn, settings=Depends(get_settings)):
    # Truncate narrative if needed (budget alignment)
    truncated = False
    max_len = 2000
    narrative = payload.narrative
    if len(narrative) > max_len:
        narrative = narrative[:max_len]
        payload.narrative = narrative
        truncated = True

    dispute_id = f"dsp_{uuid.uuid4().hex[:10]}"
    classification, enrichment, recommendation, total_latency, _audit = await process_case(dispute_id, payload)

    return DisputeOut(
        id=dispute_id,
        external_ref=payload.external_ref,
        classification=Classification(**{k: classification[k] for k in ("label", "confidence", "rationale")}),
        recommendation=Recommendation(**{k: recommendation[k] for k in ("action", "confidence", "rationale")}),
        truncated=truncated,
        latency_ms=total_latency
    )


@router.get("/disputes/{dispute_id}", response_model=DisputeOut)
async def get_dispute(dispute_id: str):
    dispute = await get_dispute_by_id(dispute_id)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    # Reconstruct output (enrichment not persisted, so use static)
    classification = Classification(
        label=dispute.classification or "OTHER",
        confidence=dispute.classification_confidence or 0.0,
        rationale=dispute.recommendation_rationale.get("rationale") if dispute.recommendation_rationale else ""
    )
    recommendation = Recommendation(
        action=dispute.recommendation_action or "ESCALATE_REVIEW",
        confidence=dispute.recommendation_confidence or 0.0,
        rationale=dispute.recommendation_rationale.get("rationale") if dispute.recommendation_rationale else ""
    )
    return DisputeOut(
        id=dispute.id,
        external_ref=dispute.external_ref,
        classification=classification,
        recommendation=recommendation,
        truncated=False,
        latency_ms=0
    )


@router.get("/disputes/{dispute_id}/audit", response_model=AuditLogOut)
async def get_dispute_audit(dispute_id: str):
    events = await get_audit_log(dispute_id)
    if not events:
        raise HTTPException(status_code=404, detail="No audit events found for this dispute")
    audit_events = [
        AuditEventOut(
            step=e.step,
            timestamp=e.created_at.timestamp(),
            latency_ms=e.payload_json.get("latency_ms", 0),
            success=e.payload_json.get("success", True),
            details={k: v for k, v in e.payload_json.items() if k not in ("latency_ms", "success", "step", "timestamp")}
        ) for e in events
    ]
    return AuditLogOut(case_id=dispute_id, events=audit_events)
