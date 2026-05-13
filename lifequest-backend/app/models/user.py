"""
User ORM-модель.
ИСПРАВЛЕНИЯ:
  - добавлены поля display_name, avatar_url, rank_title (используются в schemas/user.py)
  - добавлено поле weekly_xp (для недельного лидерборда, сбрасывается кроном)
  - добавлено поле last_active_at (используется в users.py при регистрации)
  - исправлено: поле называется gold (не coins) — users.py уже использовал gold=50
  - current_streak → streak_days (оставляем streak_days, в схемах исправляем маппинг)
"""

from sqlalchemy import String, Integer, Boolean, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from typing import Optional, List


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Profile
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    # Game stats
    character_class: Mapped[str] = mapped_column(String(50), default="Авантюрист")
    rank_title: Mapped[str] = mapped_column(String(100), default="Новобранец")
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    xp_to_next_level: Mapped[int] = mapped_column(Integer, default=100)
    gold: Mapped[int] = mapped_column(Integer, default=50)
    crystals: Mapped[int] = mapped_column(Integer, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    max_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Leaderboards (FR-7.3)
    # weekly_xp — XP, заработанный за текущую неделю. Сбрасывается каждый понедельник кроном.
    weekly_xp: Mapped[int] = mapped_column(Integer, default=0)

    # Daily limits (anticheating, FR-5.5)
    daily_xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    daily_gold_earned: Mapped[int] = mapped_column(Integer, default=0)
    daily_xp_reset_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Profile settings
    theme: Mapped[str] = mapped_column(String(10), default="dark")
    notifications_deadlines: Mapped[bool] = mapped_column(Boolean, default=True)
    notifications_evening: Mapped[bool] = mapped_column(Boolean, default=True)
    notifications_achievements: Mapped[bool] = mapped_column(Boolean, default=True)
    language: Mapped[str] = mapped_column(String(5), default="ru")

    # Equipment slots
    equipped_hat: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    equipped_armor: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    equipped_weapon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    equipped_pet: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    equipped_background: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Buffs (FR-6.8)
    xp_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    xp_multiplier_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user", lazy="select")
    achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", lazy="select"
    )
    inventory: Mapped[List["UserInventory"]] = relationship(
        "UserInventory", back_populates="user", lazy="select"
    )
    # В самом низу класса User
    buffs: Mapped[List["UserBuff"]] = relationship("UserBuff", back_populates="user", cascade="all, delete-orphan")