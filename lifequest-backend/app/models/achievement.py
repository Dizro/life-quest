"""
Модель Achievement — глобальный каталог достижений / значков.
Таблица ``achievements``.

Достижение — это шаблон; фактические разблокировки хранятся в ``user_achievements``.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user_achievement import UserAchievement


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="машинный код, например 'first_quest_completed'",
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="название для отображения",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="описание для UI",
    )
    icon_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="ссылка на иконку или эмодзи",
    )
    xp_bonus: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        comment="разовый бонус ОП при разблокировке",
    )

    # ── временные метки ──────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── связи ────────────────────────────────────────────────
    users: Mapped[List[UserAchievement]] = relationship(
        "UserAchievement",
        back_populates="achievement",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Achievement {self.code!r}>"
