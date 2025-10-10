from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Integer, Float, Boolean, JSON, ForeignKey
import datetime as dt
import uuid
from typing import Optional, List

def _uuid() -> str:
    return str(uuid.uuid4())

class Base(DeclarativeBase):
    pass

class DisputeCase(Base):
    __tablename__ = "dispute_case"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    external_ref: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    merchant_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    amount_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3))
    narrative: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="PENDING")
    
    # Classification results
    classification: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    classification_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Recommendation results
    recommendation_action: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    recommendation_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recommendation_rationale: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)
    
    # Relationships
    audit_events: Mapped[List["AuditEvent"]] = relationship("AuditEvent", back_populates="dispute_case")
    evidence_items: Mapped[List["EvidenceItem"]] = relationship("EvidenceItem", back_populates="dispute_case")

class AuditEvent(Base):
    __tablename__ = "audit_event"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    dispute_case_id: Mapped[str] = mapped_column(String, ForeignKey("dispute_case.id"))
    step: Mapped[str] = mapped_column(String)
    timestamp: Mapped[float] = mapped_column(Float)
    latency_ms: Mapped[int] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean)
    payload_json: Mapped[dict] = mapped_column(JSON)
    
    # Relationship
    dispute_case: Mapped["DisputeCase"] = relationship("DisputeCase", back_populates="audit_events")

class EvidenceItem(Base):
    __tablename__ = "evidence_item"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    dispute_case_id: Mapped[str] = mapped_column(String, ForeignKey("dispute_case.id"))
    source: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String)
    content: Mapped[dict] = mapped_column(JSON)
    fetched_at: Mapped[float] = mapped_column(Float)
    agent_run_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationship
    dispute_case: Mapped["DisputeCase"] = relationship("DisputeCase", back_populates="evidence_items")

class TransactionLedger(Base):
    __tablename__ = "transaction_ledger"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    customer_id: Mapped[str] = mapped_column(String)
    merchant_id: Mapped[str] = mapped_column(String)
    amount_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3))
    occurred_at: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String, default="COMPLETED")
    transaction_type: Mapped[str] = mapped_column(String, default="PURCHASE")
