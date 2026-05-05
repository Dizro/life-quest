"""
Централизованные FastAPI-зависимости.

ПРОБЛЕМА: В коде были два разных get_current_user:
  - app.api.v1.auth.get_current_user  (используется в tasks.py, sync.py)
  - app.api.dependencies.get_current_user  (используется в users.py)

РЕШЕНИЕ: Единственная реализация здесь. Оба модуля должны импортировать отсюда.
tasks.py и sync.py при этом нужно обновить импорт на: from app.api.dependencies import get_current_user
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Извлекает пользователя из JWT access-токена.
    Используется во всех защищённых эндпоинтах через Depends(get_current_user).
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

    return user