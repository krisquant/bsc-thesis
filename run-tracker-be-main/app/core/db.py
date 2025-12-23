from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(
    settings.db.url,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300,
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
