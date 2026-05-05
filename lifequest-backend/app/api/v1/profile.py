from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.profile import ProfileSettingsUpdate, ProfileSettingsResponse

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/settings", response_model=ProfileSettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
):
    """SCRUM-206: Получить текущие настройки профиля."""
    return ProfileSettingsResponse(
        theme=current_user.theme,
        notifications_deadlines=current_user.notifications_deadlines,
        notifications_evening=current_user.notifications_evening,
        notifications_achievements=current_user.notifications_achievements,
        language=current_user.language,
    )


@router.patch("/settings", response_model=ProfileSettingsResponse)
async def update_settings(
    data: ProfileSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    SCRUM-206: Сохранение пользовательских настроек в БД.
    Включает флаг dark/light theme — настройки не сбрасываются при перезаходе.
    """
    if data.theme is not None:
        current_user.theme = data.theme
    if data.notifications_deadlines is not None:
        current_user.notifications_deadlines = data.notifications_deadlines
    if data.notifications_evening is not None:
        current_user.notifications_evening = data.notifications_evening
    if data.notifications_achievements is not None:
        current_user.notifications_achievements = data.notifications_achievements
    if data.language is not None:
        current_user.language = data.language

    await db.commit()
    await db.refresh(current_user)

    return ProfileSettingsResponse(
        theme=current_user.theme,
        notifications_deadlines=current_user.notifications_deadlines,
        notifications_evening=current_user.notifications_evening,
        notifications_achievements=current_user.notifications_achievements,
        language=current_user.language,
    )