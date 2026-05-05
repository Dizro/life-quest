import uuid
from typing import Literal
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime


class ComplexityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EPIC = "Epic"


class EffortScoreData(BaseModel):
    value: int = Field(..., ge=1, le=20, description="Оценка сложности от 1 до 20")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность модели")
    reasoning: str = Field(..., max_length=255, description="Краткое обоснование")
    complexity_level: ComplexityLevel

    @field_validator("value", mode="before")
    @classmethod
    def clamp_value(cls, v):
        try:
            v = int(v)
        except (TypeError, ValueError):
            return 5
        return max(1, min(20, v))

    @field_validator("confidence", mode="before")
    @classmethod
    def clamp_confidence(cls, v):
        try:
            v = float(v)
        except (TypeError, ValueError):
            return 0.5
        return max(0.0, min(1.0, v))

    @field_validator("reasoning", mode="before")
    @classmethod
    def truncate_reasoning(cls, v):
        if not v or not isinstance(v, str):
            return "Оценка выполнена"
        return v[:255]


class TaskInfo(BaseModel):
    original_text: str
    detected_language: Literal["ru", "en"] = "ru"


class AIMetadata(BaseModel):
    model_version: str = "yandexgpt-5-lite"
    tokens_used: int = 0
    latency_ms: int = 0


class AIResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_info: TaskInfo
    effort_score: EffortScoreData
    metadata: AIMetadata


class EffortScoreRequest(BaseModel):
    task_id: str
    description: str = Field(..., min_length=1, max_length=2000)


class EffortScoreResponse(BaseModel):
    request_id: str
    effort_score: EffortScoreData


# Fallback defaults when AI fails
FALLBACK_EFFORT_SCORE = EffortScoreData(
    value=5,
    confidence=0.0,
    reasoning="Оценка по умолчанию (таймаут или ошибка ИИ)",
    complexity_level=ComplexityLevel.MEDIUM,
)