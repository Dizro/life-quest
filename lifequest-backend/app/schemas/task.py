from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    task_type: str = Field("regular", pattern="^(regular|daily|habit)$")
    category: str = Field("personal", pattern="^(work|health|learn|personal)$")
    deadline: Optional[datetime] = None
    # For offline sync
    client_id: Optional[str] = None
    client_created_at: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = None
    deadline: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    task_type: str
    category: str
    status: str
    effort_score: Optional[int]
    complexity_level: Optional[str]
    xp_reward: int
    gold_reward: int
    deadline: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskCompleteResponse(BaseModel):
    task: TaskResponse
    xp_gained: int
    gold_gained: int
    leveled_up: bool
    new_level: Optional[int]
    achievement_unlocked: Optional[str]
    farrix_phrase: Optional[str]