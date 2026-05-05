"""
Database engine, session factory, Base.

ИСПРАВЛЕНИЕ: users.py импортирует get_async_session, а tasks.py / sync.py — get_db.
Оба имени теперь указывают на одну и ту же функцию-генератор сессии.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.core.config import settings
from typing import AsyncGenerator


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,  # <--- Замените параметры пула на NullPool
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для FastAPI: открывает сессию, коммитит при успехе, откатывает при ошибке."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Алиас — users.py импортирует get_async_session
get_async_session = get_db