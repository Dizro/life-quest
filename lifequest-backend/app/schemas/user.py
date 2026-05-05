"""
Pydantic-схемы пользователя.

ИСПРАВЛЕНИЯ:
  - UserProfile: experience_points → xp, coins → gold, current_streak → streak_days
  - Добавлены поля display_name, avatar_url, rank_title (теперь есть в модели)
  - weekly_xp добавлен в UserProfile для лидербордов
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ── Запросы ──────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """POST /api/v1/users/ — регистрация."""
    username: str = Field(..., min_length=3, max_length=50, examples=["hero_knight"])
    email: EmailStr = Field(..., examples=["hero@lifequest.app"])
    password: str = Field(..., min_length=8, max_length=128)
    display_name: Optional[str] = Field(default=None, max_length=100)


class UserUpdate(BaseModel):
    """PATCH /api/v1/users/me — частичное обновление."""
    display_name: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=2048)


# ── Ответы ────────────────────────────────────────────────────────────────────

class UserRead(BaseModel):
    """Базовый ответ при регистрации / обновлении."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    display_name: Optional[str]
    level: int
    xp: int
    xp_to_next_level: int
    gold: int
    crystals: int
    streak_days: int
    is_active: bool
    created_at: datetime


class UserProfile(BaseModel):
    """
    GET /api/v1/users/me — расширенный профиль героя.
    Все имена полей совпадают с именами в модели User.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    rank_title: str

    # Игровые характеристики
    level: int
    xp: int
    xp_to_next_level: int
    gold: int
    crystals: int
    streak_days: int
    max_streak: int
    weekly_xp: int

    # Мета
    character_class: str
    is_active: bool
    created_at: datetime

    # Агрегаты (считаются в роуте)
    quests_completed: int = 0
    achievements_count: int = 0