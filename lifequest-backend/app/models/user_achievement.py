"""
UserAchievement — таблица-связка: какой пользователь разблокировал какое достижение.
Таблица ``user_achievements``.

Ограничения:
    - uq_user_achievement(user_id, achievement_id) — запрещает повторную разблокировку

Индексы:
    - ix_user_achievements_user_id
    - ix_user_achievements_achievement_id
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="когда пользователь разблокировал достижение",
    )

    # ── связи ────────────────────────────────────────────────
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="achievements",
        lazy="joined",
    )
    achievement: Mapped["Achievement"] = relationship(  # noqa: F821
        "Achievement",
        back_populates="users",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<UserAchievement user={self.user_id} ach={self.achievement_id}>"
