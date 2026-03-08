"""
Pydantic-схемы пользователя — контракты API для эндпоинтов /users.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ── запросы ──────────────────────────────────────────────────

class UserCreate(BaseModel):
    """POST /api/v1/users — тело запроса на регистрацию."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        examples=["hero_knight"],
        description="Уникальное имя пользователя (3–50 символов)",
    )
    email: EmailStr = Field(
        ...,
        examples=["hero@lifequest.app"],
        description="Электронная почта",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["SuperSecret123!"],
        description="Пароль (8–128 символов)",
    )
    display_name: Optional[str] = Field(
        default=None,
        max_length=100,
        examples=["Фаррикс"],
        description="Отображаемое имя персонажа",
    )


class UserUpdate(BaseModel):
    """PATCH /api/v1/users/{id} — частичное обновление профиля."""
    display_name: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=2048)


# ── ответы ───────────────────────────────────────────────────

class UserRead(BaseModel):
    """краткое представление пользователя (списки, поиск)."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    display_name: Optional[str]
    level: int
    experience_points: int
    coins: int
    rank_title: str
    is_active: bool
    created_at: datetime


class UserProfile(UserRead):
    """расширенный профиль героя — данные для экрана «Профиль»."""
    avatar_url: Optional[str] = None
    quests_completed: int = Field(default=0, description="Количество выполненных квестов")
    achievements_count: int = Field(default=0, description="Количество достижений")
    current_streak: int = Field(default=0, description="Текущая серия активных дней")
