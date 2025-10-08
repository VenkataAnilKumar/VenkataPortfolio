"""
Enhanced Database Service Module.
Handles database operations with improved async support and metrics.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.future import select
from app.domain.models import Base, DisputeCase, Merchant, Customer, Transaction
from app.telemetry.metrics import metrics
from app.core.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(settings.db_url)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class DatabaseService:
    """Enhanced database service with metrics and caching."""
    
    async def init_db(self):
        """Initialize database schema."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    async def create_dispute(
        self,
        data: Dict,
        session: Optional[AsyncSession] = None
    ) -> DisputeCase:
        """Create new dispute case with metrics."""
        async with AsyncSessionLocal() as session:
            try:
                dispute = DisputeCase(**data)
                session.add(dispute)
                await session.commit()
                await session.refresh(dispute)
                
                # Record metrics
                metrics.record_dispute(
                    status="CREATED",
                    dispute_type=data.get("type", "UNKNOWN")
                )
                
                return dispute
                
            except Exception as e:
                await session.rollback()
                raise
                
    async def get_dispute(
        self,
        dispute_id: str,
        session: Optional[AsyncSession] = None
    ) -> Optional[DisputeCase]:
        """Get dispute by ID."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(DisputeCase).filter(DisputeCase.id == dispute_id)
            )
            return result.scalar_one_or_none()
            
    async def get_disputes(
        self,
        merchant_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[DisputeCase]:
        """Get disputes with filters."""
        async with AsyncSessionLocal() as session:
            query = select(DisputeCase)
            
            if merchant_id:
                query = query.filter(DisputeCase.merchant_id == merchant_id)
            if customer_id:
                query = query.filter(DisputeCase.customer_id == customer_id)
            if start_date:
                query = query.filter(DisputeCase.created_at >= start_date)
                
            query = query.limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
            
    async def update_dispute(
        self,
        dispute_id: str,
        updates: Dict,
        session: Optional[AsyncSession] = None
    ) -> Optional[DisputeCase]:
        """Update dispute with metrics."""
        async with AsyncSessionLocal() as session:
            dispute = await self.get_dispute(dispute_id, session)
            if not dispute:
                return None
                
            # Apply updates
            for key, value in updates.items():
                setattr(dispute, key, value)
                
            # Record resolution time if status changes to RESOLVED
            if updates.get("status") == "RESOLVED":
                resolution_time = (datetime.now() - dispute.created_at).total_seconds()
                metrics.record_resolution_time(resolution_time)
                
            await session.commit()
            await session.refresh(dispute)
            return dispute
