"""
Mock-эндпоинты пользователей.
Возвращают захардкоженные данные, чтобы фронтенд мог начать интеграцию сразу.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.user import UserCreate, UserRead, UserUpdate, UserProfile

router = APIRouter()

# ── тестовые данные ──────────────────────────────────────────

_MOCK_USER_ID = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
_MOCK_NOW = datetime(2026, 3, 5, 12, 0, 0, tzinfo=timezone.utc)

_MOCK_USER = UserRead(
    id=_MOCK_USER_ID,
    username="hero_knight",
    email="hero@lifequest.app",
    display_name="Фаррикс",
    level=2,
    experience_points=135,
    coins=42,
    rank_title="Путешественник",
    is_active=True,
    created_at=_MOCK_NOW,
)

_MOCK_PROFILE = UserProfile(
    **_MOCK_USER.model_dump(),
    avatar_url="https://api.lifequest.app/avatars/hero_knight.png",
    quests_completed=12,
    achievements_count=3,
    current_streak=5,
)


# ── эндпоинты ───────────────────────────────────────────────

@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создаёт аккаунт игрока и возвращает его данные.",
)
async def create_user(body: UserCreate) -> UserRead:
    """mock: игнорирует тело, возвращает захардкоженного пользователя."""
    return _MOCK_USER


@router.get(
    "/",
    response_model=list,
    summary="Список пользователей",
    description="Возвращает постраничный список пользователей (mock: один пользователь).",
)
async def list_users(page: int = 1, size: int = 20):
    return [_MOCK_USER]


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Получить пользователя по ID",
    description="Возвращает данные пользователя по его UUID.",
)
async def get_user(user_id: uuid.UUID) -> UserRead:
    if user_id != _MOCK_USER_ID:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return _MOCK_USER


@router.get(
    "/{user_id}/profile",
    response_model=UserProfile,
    summary="Профиль героя",
    description="Расширенный профиль с RPG-статистикой для экрана «Профиль».",
)
async def get_user_profile(user_id: uuid.UUID) -> UserProfile:
    if user_id != _MOCK_USER_ID:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return _MOCK_PROFILE


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Обновить профиль",
    description="Частичное обновление данных пользователя.",
)
async def update_user(user_id: uuid.UUID, body: UserUpdate) -> UserRead:
    if user_id != _MOCK_USER_ID:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    data = _MOCK_USER.model_dump()
    update = body.model_dump(exclude_unset=True)
    data.update(update)
    return UserRead(**data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить аккаунт",
    description="Удаляет пользователя и все связанные данные.",
    response_class=Response,
)
async def delete_user(user_id: uuid.UUID):
    if user_id != _MOCK_USER_ID:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
