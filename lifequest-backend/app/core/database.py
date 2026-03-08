"""
Асинхронный движок SQLAlchemy и фабрика сессий для PostgreSQL 15.

Использование в эндпоинтах:
    from app.core.database import get_async_session
    async def endpoint(session: AsyncSession = Depends(get_async_session)):
        ...
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# ── движок (connection pool) ─────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,          # переподключение при разрыве
    pool_recycle=1800,            # пересоздание соединений каждые 30 мин
)

# ── фабрика сессий ───────────────────────────────────────────
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── базовый класс для всех ORM-моделей ──────────────────────
class Base(DeclarativeBase):
    """декларативная база для наследования всеми моделями."""
    pass


# ── зависимость FastAPI ──────────────────────────────────────
async def get_async_session() -> AsyncSession:  # type: ignore[misc]
    """отдаёт асинхронную сессию; коммитит при успехе, откатывает при ошибке."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
