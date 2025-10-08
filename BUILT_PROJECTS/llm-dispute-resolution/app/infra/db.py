from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from . import db_state
from ..core.config import get_settings
from ..domain.models import Base


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


async def get_session() -> AsyncSession:
    if not db_state.session_maker:
        await init_db()
    assert db_state.session_maker
    async with db_state.session_maker() as session:
        yield session
