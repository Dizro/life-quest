"""
Модель DeviceToken — хранит push-токены устройств пользователей.
Таблица ``device_tokens``.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class DeviceToken(Base):
    __tablename__ = "device_tokens"
    __table_args__ = (
        UniqueConstraint("user_id", "token", name="uq_user_device_token"),
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
    token: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        comment="FCM/APNS/WebPush токен устройства",
    )
    platform: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="ios / android / web",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Связь с пользователем
    user: Mapped[User] = relationship(
        "User",
        back_populates="device_tokens",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<DeviceToken user={self.user_id} platform={self.platform}>"