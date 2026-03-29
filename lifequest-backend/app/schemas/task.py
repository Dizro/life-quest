"""
Pydantic-схемы задач (квестов) — контракты API для эндпоинтов /tasks.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


# ── перечисления ──────────────────────────────────────────────────────────────

class TaskStatusEnum(str, Enum):
    PENDING_ES = "pending_es"  # ожидает ИИ-оценки ES
    ACTIVE = "active"
    COMPLETED = "completed"
    TRIAL = "trial"        # было FAILED — исправлено
    REDEEMED = "redeemed"  # добавлено
    ARCHIVED = "archived"


class TaskTypeEnum(str, Enum):  # добавлено для нового поля task_type
    REGULAR = "regular"
    DAILY = "daily"
    HABIT = "habit"


class TaskPriorityEnum(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"


class TaskRecurrenceEnum(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TaskCategoryEnum(str, Enum):
    WORK = "work"
    HEALTH = "health"
    STUDY = "study"
    CREATIVITY = "creativity"
    FAMILY = "family"
    OTHER = "other"


# ── запросы ───────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    """POST /api/v1/tasks — создание нового квеста."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["Утренняя медитация"],
        description="Название квеста",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=4000,
        examples=["15 минут медитации перед завтраком"],
        description="Развёрнутое описание (поддерживается markdown)",
    )
    task_type: TaskTypeEnum = Field(
        default=TaskTypeEnum.REGULAR,
        description="Тип задачи: обычная / ежедневная / привычка",
    )
    priority: TaskPriorityEnum = Field(
        default=TaskPriorityEnum.COMMON,
        description="Редкость / приоритет",
    )
    category: TaskCategoryEnum = Field(
        default=TaskCategoryEnum.OTHER,
        description="Категория — сфера жизни",
    )
    recurrence: TaskRecurrenceEnum = Field(
        default=TaskRecurrenceEnum.NONE,
        description="Повторение квеста",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        examples=["2026-03-15T23:59:59Z"],
        description="Дедлайн (ISO 8601, с часовым поясом)",
    )
    xp_reward: int = Field(default=10, ge=1, le=1000, description="Награда в очках опыта")
    coin_reward: int = Field(default=1, ge=0, le=500, description="Награда в монетах")


class TaskUpdate(BaseModel):
    """PATCH /api/v1/tasks/{id} — частичное обновление квеста."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=4000)
    priority: Optional[TaskPriorityEnum] = None
    category: Optional[TaskCategoryEnum] = None
    recurrence: Optional[TaskRecurrenceEnum] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatusEnum] = None


class TaskComplete(BaseModel):
    """POST /api/v1/tasks/{id}/complete — ответ после выполнения квеста."""
    model_config = ConfigDict(from_attributes=True)

    task_id: uuid.UUID
    xp_earned: int
    coins_earned: int
    new_total_xp: int
    new_level: int
    new_rank_title: str
    leveled_up: bool = Field(default=False, description="Был ли повышен уровень")
    achievement_unlocked: Optional[str] = Field(
        default=None,
        description="Код разблокированного достижения (если есть)",
    )


# ── ответы ────────────────────────────────────────────────────────────────────

class TaskRead(BaseModel):
    """представление одного квеста."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    description: Optional[str]
    task_type: TaskTypeEnum
    status: TaskStatusEnum
    priority: TaskPriorityEnum
    category: TaskCategoryEnum
    recurrence: TaskRecurrenceEnum
    effort_score: Optional[int]
    xp_reward: int
    coin_reward: int
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    trial_since: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """постраничный список квестов."""
    total: int
    page: int
    size: int
    items: List[TaskRead]