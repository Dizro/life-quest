from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AchievementResponse(BaseModel):
    id: int
    key: str
    name: str
    description: str
    icon: str
    crystal_reward: int
    xp_reward: int
    condition_type: str
    condition_value: int
    unlocked: bool
    unlocked_at: Optional[datetime]
    progress: Optional[float] = None  # 0.0 - 1.0

    model_config = {"from_attributes": True}


class AchievementsListResponse(BaseModel):
    unlocked: list[AchievementResponse]
    locked: list[AchievementResponse]
    total_unlocked: int
    total: int