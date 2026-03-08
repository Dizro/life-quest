"""Mock-эндпоинты достижений."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.schemas.achievement import AchievementRead, UserAchievementRead

router = APIRouter()

# ── тестовые данные ──────────────────────────────────────────

_MOCK_ACHIEVEMENTS: list = [
    AchievementRead(
        id=uuid.UUID("aaaa1111-1111-1111-1111-111111111111"),
        code="first_quest_completed",
        title="Первая стезя",
        description="Выполните свой первый квест.",
        icon_url="🏅",
        xp_bonus=15,
    ),
    AchievementRead(
        id=uuid.UUID("aaaa2222-2222-2222-2222-222222222222"),
        code="streak_7_days",
        title="Пламя дисциплины",
        description="Выполняйте квесты 7 дней подряд.",
        icon_url="🔥",
        xp_bonus=50,
    ),
    AchievementRead(
        id=uuid.UUID("aaaa3333-3333-3333-3333-333333333333"),
        code="level_5_reached",
        title="Искатель",
        description="Достигните 5-го уровня.",
        icon_url="⭐",
        xp_bonus=100,
    ),
]

_NOW = datetime(2026, 3, 5, 12, 0, 0, tzinfo=timezone.utc)

_MOCK_USER_ACHIEVEMENTS: list = [
    UserAchievementRead(
        id=uuid.UUID("bbbb1111-1111-1111-1111-111111111111"),
        achievement=_MOCK_ACHIEVEMENTS[0],
        unlocked_at=_NOW,
    ),
]


# ── эндпоинты ───────────────────────────────────────────────

@router.get(
    "/",
    response_model=list,
    summary="Каталог достижений",
    description="Возвращает полный список доступных достижений в игре.",
)
async def list_achievements():
    return _MOCK_ACHIEVEMENTS


@router.get(
    "/{achievement_id}",
    response_model=AchievementRead,
    summary="Получить достижение по ID",
    description="Возвращает информацию о конкретном достижении.",
)
async def get_achievement(achievement_id: uuid.UUID) -> AchievementRead:
    for a in _MOCK_ACHIEVEMENTS:
        if a.id == achievement_id:
            return a
    raise HTTPException(status_code=404, detail="Достижение не найдено")


@router.get(
    "/user/{user_id}",
    response_model=list,
    summary="Достижения пользователя",
    description="Возвращает список разблокированных достижений конкретного пользователя.",
)
async def list_user_achievements(user_id: uuid.UUID):
    return _MOCK_USER_ACHIEVEMENTS
