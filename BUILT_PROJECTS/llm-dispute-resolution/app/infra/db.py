from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from ..core.config import get_settings
from ..domain.models import Base
from contextlib import asynccontextmanager

class DBState:
    engine = None
    session_maker: async_sessionmaker[AsyncSession] | None = None

db_state = DBState()

async def init_db():
    settings = get_settings()
    if not db_state.engine:
        db_state.engine = create_async_engine(settings.db_url, echo=False)
        db_state.session_maker = async_sessionmaker(db_state.engine, expire_on_commit=False)
        async with db_state.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def get_session():
    if not db_state.session_maker:
        await init_db()
    assert db_state.session_maker
    async with db_state.session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_db():
    """FastAPI dependency for database session"""
    async with get_session() as session:
        yield session
