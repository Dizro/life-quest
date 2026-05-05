from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from typing import Optional


class UserInventory(Base):
    __tablename__ = "user_inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    item_key: Mapped[str] = mapped_column(String(100), index=True)
    item_type: Mapped[str] = mapped_column(String(30))  # hat | armor | weapon | pet | background | buff
    item_name: Mapped[str] = mapped_column(String(200), default="")
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # For buffs
    buff_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="inventory")