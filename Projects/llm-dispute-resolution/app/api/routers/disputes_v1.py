from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.schemas import DisputeIn, DisputeOut, Classification, Recommendation, MetricsOut, AuditLogOut, AuditEventOut
from app.services.orchestrator import process_case, get_dispute_by_id, get_audit_log
from app.infra.db import get_db
from app.telemetry.metrics import metrics
from app.telemetry.audit import get_audit_events
import uuid
import time

router = APIRouter(prefix="/v1", tags=["disputes-v1"])

def generate_dispute_id() -> str:
    return f"dsp_{str(uuid.uuid4())}"

@router.post("/disputes", response_model=DisputeOut)
async def create_dispute(dispute_in: DisputeIn, db: AsyncSession = Depends(get_db)):
    """
    Create and process a new dispute case through the full pipeline:
    1. Classification
    2. Enrichment  
    3. Recommendation
    """
    try:
        dispute_id = generate_dispute_id()
        
        # Process through the orchestrator
        classification, enrichment, recommendation, total_latency_ms, audit_events = await process_case(dispute_id, dispute_in)
        
        # Build response
        classification_obj = Classification(
            label=classification.get("label", "UNKNOWN"),
            confidence=classification.get("confidence", 0.0),
            rationale=classification.get("rationale", "")
        )
        
        recommendation_obj = Recommendation(
            action=recommendation.get("action", "ESCALATE_REVIEW"),
            confidence=recommendation.get("confidence", 0.0),
            rationale=recommendation.get("rationale", "")
        )
        
        return DisputeOut(
            id=dispute_id,
            external_ref=dispute_in.external_ref,
            classification=classification_obj,
            recommendation=recommendation_obj,
            truncated=False,
            latency_ms=total_latency_ms
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing dispute: {str(e)}")

@router.get("/disputes/{dispute_id}", response_model=DisputeOut)
async def get_dispute(dispute_id: str):
    """Get a dispute case by ID"""
    try:
        dispute = await get_dispute_by_id(dispute_id)
        if not dispute:
            raise HTTPException(status_code=404, detail="Dispute not found")
        
        classification_obj = Classification(
            label=dispute.classification or "UNKNOWN",
            confidence=dispute.classification_confidence or 0.0,
            rationale="Stored classification result"
        )
        
        recommendation_obj = Recommendation(
            action=dispute.recommendation_action or "ESCALATE_REVIEW",
            confidence=dispute.recommendation_confidence or 0.0,
            rationale=dispute.recommendation_rationale.get("rationale", "") if dispute.recommendation_rationale else ""
        )
        
        return DisputeOut(
            id=dispute.id,
            external_ref=dispute.external_ref,
            classification=classification_obj,
            recommendation=recommendation_obj,
            truncated=False,
            latency_ms=0  # Not available for stored disputes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dispute: {str(e)}")

@router.get("/disputes/{dispute_id}/audit", response_model=AuditLogOut)
async def get_dispute_audit_log(dispute_id: str):
    """Get the audit log for a dispute case"""
    try:
        audit_events = await get_audit_log(dispute_id)
        
        events = [
            AuditEventOut(
                step=event.step,
                timestamp=event.timestamp,
                latency_ms=event.latency_ms,
                success=event.success,
                details=event.payload_json.get("details") if event.payload_json else None
            )
            for event in audit_events
        ]
        
        return AuditLogOut(
            case_id=dispute_id,
            events=events
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audit log: {str(e)}")

@router.get("/metrics", response_model=MetricsOut)
async def get_metrics():
    """Get system metrics"""
    return metrics.snapshot()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}