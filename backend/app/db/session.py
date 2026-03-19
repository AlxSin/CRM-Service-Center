from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from collections.abc import AsyncGenerator

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator:
    # FastAPI dependency: provides a transactional SQLAlchemy AsyncSession.
    async with AsyncSessionLocal() as session:
        yield session