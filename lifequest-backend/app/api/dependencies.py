"""
Централизованные FastAPI-зависимости.

ПРОБЛЕМА: В коде были два разных get_current_user:
  - app.api.v1.auth.get_current_user  (используется в tasks.py, sync.py)
  - app.api.dependencies.get_current_user  (используется в users.py)

РЕШЕНИЕ: Единственная реализация здесь. Оба модуля должны импортировать отсюда.
tasks.py и sync.py при этом нужно обновить импорт на: from app.api.dependencies import get_current_user
"""

import logging
from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.user_buff import UserBuff

logger = logging.getLogger(__name__)
security = HTTPBearer()

RESURRECTION_ABSENCE_DAYS = 7


async def _check_resurrection(user: User, db: AsyncSession) -> None:
    """
    Воскрешение (FR-6.6, UC-23) — автоматический серверный триггер.
    Если пользователь не заходил ≥7 дней:
      1. Все active + trial задачи → archived (Забытые легенды)
      2. Стрик → 0 (max_streak сохраняется)
      3. Бафф ×2.0 XP на 3 дня
    """
    if not user.last_active_at:
        return

    days_absent = (datetime.now(timezone.utc) - user.last_active_at).days
    if days_absent < RESURRECTION_ABSENCE_DAYS:
        return

    logger.info("Resurrection triggered for user %s (absent %s days)", user.id, days_absent)

    # 1. Архивируем все active + trial задачи
    await db.execute(
        update(Task)
        .where(
            Task.user_id == user.id,
            Task.status.in_(["active", "trial"]),
        )
        .values(status="archived")
    )

    # 2. Стрик сбрасывается, рекорд сохраняется
    user.streak_days = 0

    # 3. Бафф воскрешения ×2.0 XP на 3 дня
    now = datetime.now(timezone.utc)
    buff = UserBuff(
        user_id=user.id,
        buff_type="xp_boost",
        multiplier=2.0,
        expires_at=now + timedelta(days=3),
    )
    db.add(buff)

    # Обновляем множитель на User для быстрого доступа
    user.xp_multiplier = 2.0
    user.xp_multiplier_expires = now + timedelta(days=3)

    await db.flush()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Извлекает пользователя из JWT access-токена.
    При каждом запросе проверяет условие воскрешения (≥7 дней отсутствия).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type", "access")

        if user_id is None or token_type != "access":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    # Проверка воскрешения (серверный триггер — не кнопка)
    await _check_resurrection(user, db)

    # Обновляем last_active_at
    user.last_active_at = datetime.now(timezone.utc)
    await db.commit()

    return user