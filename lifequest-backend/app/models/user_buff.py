"""
Модель UserBuff — представляет баффы пользователя.
Таблица ``user_buffs``.

Индексы:
    - ix_user_buffs_user_id
    - ix_user_buffs_buff_type
    - ix_user_buffs_expires_at
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserBuff(Base):
    __tablename__ = "user_buffs"

    # ИСПРАВЛЕНО: Теперь id — это целое число (Integer), автоинкремент
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ИСПРАВЛЕНО: user_id теперь тоже целое число, чтобы совпадать с users.id
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    buff_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="тип баффа (например, 'xp_boost')",
    )

    multiplier: Mapped[float] = mapped_column(
        Numeric(4, 2),
        default=1.0,
        server_default="1.0",
        nullable=False,
        comment="множитель баффа",
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="дата и время истечения баффа",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── связи ────────────────────────────────────────────────
    user: Mapped["User"] = relationship(
        "User",
        back_populates="buffs",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<UserBuff {self.buff_type!r} x{self.multiplier}>"