"""
Модель User — представляет игрока в системе LifeQuest.
Таблица ``users``.

Индексы:
    - ix_users_email        (уникальный)
    - ix_users_username      (уникальный)
    - ix_users_created_at

Связи:
    - tasks          → Task (один-ко-многим, back_populates="owner")
    - achievements   → UserAchievement (один-ко-многим)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user_achievement import UserAchievement
    from app.models.user_buff import UserBuff


class User(Base):
    __tablename__ = "users"

    # ── первичный ключ ───────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
        comment="уникальный идентификатор пользователя (UUID v4)",
    )

    # ── учётные данные ───────────────────────────────────────
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="уникальный логин",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="электронная почта",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="хеш пароля (bcrypt / argon2)",
    )

    # ── профиль / RPG ───────────────────────────────────────
    display_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="отображаемое имя персонажа",
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="ссылка на аватар",
    )
    level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
        nullable=False,
        comment="текущий уровень игрока",
    )
    experience_points: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        comment="общее количество очков опыта",
    )
    coins: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        comment="баланс внутриигровой валюты",
    )
    rank_title: Mapped[str] = mapped_column(
        String(100),
        default="Новичок",
        server_default="Новичок",
        nullable=False,
        comment="текущее звание / титул",
    )

    # ── флаги ────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    # ── игровые метрики ──────────────────────────────────────
    crystals: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        comment="премиум-валюта (кристаллы)",
    )
    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        comment="текущая серия дней без пропусков",
    )
    best_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        comment="максимальная серия дней",
    )

    # ── активность и онбординг ───────────────────────────────
    last_active_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="время последней активности пользователя",
    )
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        comment="флаг завершения онбординга",
    )

    # ── временные метки ──────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="дата создания записи (UTC)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="дата последнего обновления (UTC)",
    )

    # ── связи ────────────────────────────────────────────────
    tasks: Mapped[List[Task]] = relationship(
        "Task",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    achievements: Mapped[List[UserAchievement]] = relationship(
        "UserAchievement",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    buffs: Mapped[List[UserBuff]] = relationship(
        "UserBuff",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User {self.username!r} lvl={self.level}>"
