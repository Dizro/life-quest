"""
Эндпоинты достижений.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_async_session
from app.models.achievement import Achievement
from app.models.user_achievement import UserAchievement
from app.models.user import User
from app.schemas.achievement import AchievementRead, UserAchievementRead
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get(
    "/",
    response_model=list[AchievementRead],
    summary="Каталог достижений",
    description="Полный список доступных достижений в игре."
)
async def list_achievements(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user) # Требует авторизацию
):
    result = await session.execute(select(Achievement))
    return result.scalars().all()


@router.get(
    "/{achievement_id}",
    response_model=AchievementRead,
    summary="Получить достижение по ID",
)
async def get_achievement(
    achievement_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> AchievementRead:
    result = await session.execute(select(Achievement).where(Achievement.id == achievement_id))
    achievement = result.scalar_one_or_none()
    if not achievement:
        raise HTTPException(status_code=404, detail="Достижение не найдено")
    return achievement


@router.get(
    "/user/me",
    response_model=list[UserAchievementRead],
    summary="Мои достижения",
    description="Возвращает список разблокированных достижений текущего пользователя."
)
async def list_my_achievements(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    # Используем selectinload для жадной загрузки связанного объекта achievement
    query = (
        select(UserAchievement)
        .where(UserAchievement.user_id == current_user.id)
        .options(selectinload(UserAchievement.achievement))
    )
    result = await session.execute(query)
    return result.scalars().all()