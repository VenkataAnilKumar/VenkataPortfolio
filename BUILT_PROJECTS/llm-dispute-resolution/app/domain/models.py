from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Text, JSON, DateTime
import datetime as dt
import uuid


def _uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class DisputeCase(Base):
    __tablename__ = "dispute_case"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    external_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    customer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    merchant_id: Mapped[str | None] = mapped_column(String, nullable=True)
    amount_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3))
    narrative: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="RECEIVED")
    classification: Mapped[str | None] = mapped_column(String, nullable=True)
    classification_confidence: Mapped[float | None] = mapped_column(Integer, nullable=True)
    recommendation_action: Mapped[str | None] = mapped_column(String, nullable=True)
    recommendation_confidence: Mapped[float | None] = mapped_column(Integer, nullable=True)
    recommendation_rationale: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_event"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    dispute_case_id: Mapped[str] = mapped_column(String)
    step: Mapped[str] = mapped_column(String)
    payload_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
