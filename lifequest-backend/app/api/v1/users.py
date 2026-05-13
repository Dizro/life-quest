"""
Эндпоинты пользователей.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.models.user_buff import UserBuff
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserProfile, PasswordChange
from app.api.dependencies import get_current_user

router = APIRouter(tags=["users"])   # ← УБРАЛИ prefix="/users"


@router.get(
    "/me",
    response_model=UserProfile,
)
async def get_my_profile(current_user: User = Depends(get_current_user)) -> UserProfile:
    """Получить профиль текущего пользователя"""
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        rank_title=current_user.rank_title,
        level=current_user.level,
        xp=current_user.xp,
        xp_to_next_level=current_user.xp_to_next_level,
        gold=current_user.gold,
        crystals=current_user.crystals,
        streak_days=current_user.streak_days,
        max_streak=current_user.max_streak,
        weekly_xp=getattr(current_user, 'weekly_xp', 0),
        character_class=current_user.character_class,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        theme=current_user.theme,
        language=current_user.language,
        notifications_deadlines=current_user.notifications_deadlines,
        notifications_evening=current_user.notifications_evening,
        notifications_achievements=current_user.notifications_achievements,
        quests_completed=0,
        achievements_count=0,
    )


@router.patch("/me", response_model=UserRead)
async def update_my_profile(
    body: UserUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserRead:
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.post("/me/password")
async def change_password(
    body: PasswordChange,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Смена пароля."""
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")
    current_user.hashed_password = get_password_hash(body.new_password)
    session.add(current_user)
    await session.commit()
    return {"success": True, "message": "Пароль изменён"}


@router.delete("/me")
async def delete_account(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удаление аккаунта."""
    await session.delete(current_user)
    await session.commit()
    return {"success": True, "message": "Аккаунт удалён"}