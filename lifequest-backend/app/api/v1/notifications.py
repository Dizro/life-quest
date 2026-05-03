"""
Эндпоинты для управления push-уведомлениями (регистрация/удаление токенов).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.device_token import DeviceToken

router = APIRouter()


class RegisterTokenRequest(BaseModel):
    token: str
    platform: str  # 'ios', 'android', 'web'


class UnregisterTokenRequest(BaseModel):
    token: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_device_token(
    body: RegisterTokenRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Регистрирует push-токен для текущего пользователя.
    Если токен уже существует, обновляет платформу и updated_at.
    """
    # Проверка допустимой платформы
    if body.platform not in ("ios", "android", "web"):
        raise HTTPException(
            status_code=400, detail="Platform must be one of: ios, android, web"
        )

    # Ищем существующий токен
    result = await session.execute(
        select(DeviceToken).where(
            DeviceToken.user_id == current_user.id,
            DeviceToken.token == body.token,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Обновляем платформу и время
        existing.platform = body.platform
        existing.updated_at = func.now()
        await session.commit()
        return {"status": "updated", "token": body.token}
    else:
        # Создаём новый
        new_token = DeviceToken(
            user_id=current_user.id,
            token=body.token,
            platform=body.platform,
        )
        session.add(new_token)
        await session.commit()
        return {"status": "registered", "token": body.token}


@router.delete("/unregister", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_device_token(
    body: UnregisterTokenRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Удаляет push-токен текущего пользователя.
    """
    result = await session.execute(
        select(DeviceToken).where(
            DeviceToken.user_id == current_user.id,
            DeviceToken.token == body.token,
        )
    )
    token_entry = result.scalar_one_or_none()
    if token_entry:
        await session.delete(token_entry)
        await session.commit()
    # Если токен не найден, всё равно возвращаем 204 (успех)
    return