import time
from ..domain.schemas import DisputeIn
from .classifier import run_classification
from .enrichment import run_enrichment
from .recommendation import run_recommendation
from ..telemetry.metrics import metrics
from ..telemetry.audit import get_audit_events, flush_audit_events
from ..infra.db import get_session
from ..domain.models import DisputeCase, AuditEvent
from sqlalchemy import select

async def process_case(dispute_id: str, payload: DisputeIn):
    t0 = time.perf_counter()

    classification = await run_classification(payload.narrative, payload.amount, payload.currency)
    enrichment = await run_enrichment(dispute_id)
    recommendation = await run_recommendation(classification, enrichment)

    metrics.record_classification_latency(classification.get("latency_ms", 0))
    metrics.record_recommendation_latency(recommendation.get("latency_ms", 0))
    metrics.increment_case(classification.get("label"))
    # Track total LLM cost for this case (classification + recommendation)
    total_cost = float(classification.get("cost_usd", 0.0)) + float(recommendation.get("cost_usd", 0.0))
    metrics.record_case_cost(total_cost)

    # Persist dispute and audit events
    async for session in get_session():
        dispute = DisputeCase(
            id=dispute_id,
            external_ref=payload.external_ref,
            customer_id=payload.customer_id,
            merchant_id=payload.merchant_id,
            amount_cents=payload.amount,
            currency=payload.currency,
            narrative=payload.narrative,
            status="COMPLETED",
            classification=classification.get("label"),
            classification_confidence=classification.get("confidence"),
            recommendation_action=recommendation.get("action"),
            recommendation_confidence=recommendation.get("confidence"),
            recommendation_rationale={"rationale": recommendation.get("rationale")},
        )
        session.add(dispute)
        # Persist audit events
        audit_events = flush_audit_events(dispute_id)
        for event in audit_events:
            session.add(AuditEvent(
                dispute_case_id=dispute_id,
                step=event["step"],
                payload_json=event,
            ))
        await session.commit()

    total_latency_ms = int((time.perf_counter() - t0) * 1000)
    return classification, enrichment, recommendation, total_latency_ms, audit_events

async def get_dispute_by_id(dispute_id: str):
    async for session in get_session():
        stmt = select(DisputeCase).where(DisputeCase.id == dispute_id)
        result = await session.execute(stmt)
        dispute = result.scalar_one_or_none()
        return dispute

async def get_audit_log(dispute_id: str):
    async for session in get_session():
        stmt = select(AuditEvent).where(AuditEvent.dispute_case_id == dispute_id)
        result = await session.execute(stmt)
        return [row for row in result.scalars()]
