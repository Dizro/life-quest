from sqlalchemy import String, Integer, Boolean, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from typing import Optional


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Type: regular | daily | habit
    task_type: Mapped[str] = mapped_column(String(20), default="regular")
    # Category: work | health | learn | personal
    category: Mapped[str] = mapped_column(String(30), default="personal")

    # Status: pending_es | active | completed | trial | archived | failed
    status: Mapped[str] = mapped_column(String(20), default="pending_es", index=True)

    # AI Effort Score (SCRUM-212)
    effort_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    effort_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    effort_reasoning: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    complexity_level: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # Low|Medium|High|Epic

    # Rewards (calculated from effort_score)
    xp_reward: Mapped[int] = mapped_column(Integer, default=0)
    gold_reward: Mapped[int] = mapped_column(Integer, default=0)

    # Anticheating
    is_duplicate_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_count: Mapped[int] = mapped_column(Integer, default=0)  # for habits

    # Deadlines
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Offline sync (SCRUM-207)
    client_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    created_offline: Mapped[bool] = mapped_column(Boolean, default=False)
    client_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Trial
    trial_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    redeem_cost: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tasks")