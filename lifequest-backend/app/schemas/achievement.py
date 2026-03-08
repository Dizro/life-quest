"""Pydantic-схемы достижений."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AchievementRead(BaseModel):
    """элемент каталога достижений."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    title: str
    description: Optional[str]
    icon_url: Optional[str]
    xp_bonus: int


class UserAchievementRead(BaseModel):
    """достижение, разблокированное конкретным пользователем."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    achievement: AchievementRead
    unlocked_at: datetime
