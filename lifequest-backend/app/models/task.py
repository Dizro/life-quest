"""
Модель Task (квест) — представляет задачу игрока.
Таблица ``tasks``.

Индексы:
    - ix_tasks_owner_id
    - ix_tasks_status
    - ix_tasks_due_date
    - ix_tasks_category
    - ix_tasks_created_at

Связи:
    - owner  → User (многие-к-одному, back_populates="tasks")
    - parent → Task (один-ко-многим, adjacency list)
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


# ── перечисления ─────────────────────────────────────────────

class TaskStatus(str, enum.Enum):
    """жизненный цикл квеста."""
    ACTIVE = "active"
    COMPLETED = "completed"
    TRIAL = "trial"
    REDEEMED = "redeemed"
    ARCHIVED = "archived"


class TaskPriority(str, enum.Enum):
    """редкость / приоритет квеста."""
    COMMON = "common"         # обычная
    UNCOMMON = "uncommon"     # необычная
    RARE = "rare"             # редкая
    EPIC = "epic"             # эпическая


class TaskRecurrence(str, enum.Enum):
    """паттерн повторения."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TaskCategory(str, enum.Enum):
    """категории — сферы жизни (маппятся на RPG-характеристики)."""
    WORK = "work"             # интеллект
    HEALTH = "health"         # сила
    STUDY = "study"           # мудрость
    CREATIVITY = "creativity" # харизма
    FAMILY = "family"         # дух
    OTHER = "other"


# ── модель ───────────────────────────────────────────────────

class Task(Base):
    __tablename__ = "tasks"

    # ── первичный ключ ───────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
        comment="уникальный идентификатор квеста (UUID v4)",
    )

    # ── внешний ключ ─────────────────────────────────────────
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK → users.id",
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK → tasks.id (подзадачи)",
    )

    # ── основные поля ────────────────────────────────────────
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="название квеста",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="расширенное описание (поддерживается markdown)",
    )

# ── RPG-атрибуты ─────────────────────────────────────────
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status", values_callable=lambda obj: [e.value for e in obj], create_constraint=True),
        default=TaskStatus.ACTIVE,
        server_default=TaskStatus.ACTIVE.value,
        nullable=False,
        index=True,
        comment="текущий статус квеста",
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, name="task_priority", values_callable=lambda obj: [e.value for e in obj], create_constraint=True),
        default=TaskPriority.COMMON,
        server_default=TaskPriority.COMMON.value,
        nullable=False,
        comment="редкость / приоритет",
    )
    category: Mapped[TaskCategory] = mapped_column(
        Enum(TaskCategory, name="task_category", values_callable=lambda obj: [e.value for e in obj], create_constraint=True),
        default=TaskCategory.OTHER,
        server_default=TaskCategory.OTHER.value,
        nullable=False,
        index=True,
        comment="категория — сфера жизни",
    )
    recurrence: Mapped[TaskRecurrence] = mapped_column(
        Enum(TaskRecurrence, name="task_recurrence", values_callable=lambda obj: [e.value for e in obj], create_constraint=True),
        default=TaskRecurrence.NONE,
        server_default=TaskRecurrence.NONE.value,
        nullable=False,
        comment="паттерн повторения",
    )

    # ── награды ──────────────────────────────────────────────
    xp_reward: Mapped[int] = mapped_column(
        Integer,
        default=10,
        server_default="10",
        nullable=False,
        comment="ОП за выполнение",
    )
    coin_reward: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
        nullable=False,
        comment="монеты за выполнение",
    )

    # ── даты ─────────────────────────────────────────────────
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="дедлайн квеста",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="когда квест был выполнен",
    )
    trial_since: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="дата перехода в статус испытания",
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
    owner: Mapped[User] = relationship(
        "User",
        back_populates="tasks",
        lazy="joined",
    )
    children: Mapped[list[Task]] = relationship(
        "Task",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    parent: Mapped[Optional[Task]] = relationship(
        "Task",
        back_populates="children",
        remote_side=[id],
    )

    def __repr__(self) -> str:
        return f"<Task {self.title!r} status={self.status.value}>"
