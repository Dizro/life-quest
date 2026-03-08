"""общие Pydantic-схемы: health-check, пагинация, ошибки."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ── health-check ─────────────────────────────────────────────

class HealthResponse(BaseModel):
    """ответ GET /health."""
    status: str = Field(example="ok")
    message: str = Field(example="LifeQuest API работает")


# ── пагинация ────────────────────────────────────────────────

class PaginationParams(BaseModel):
    """параметры пагинации из query-строки."""
    page: int = Field(default=1, ge=1, description="Номер страницы (начинается с 1)")
    size: int = Field(default=20, ge=1, le=100, description="Количество элементов на странице")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    """обёртка для постраничных списков."""
    total: int = Field(description="Общее количество элементов")
    page: int
    size: int
    items: list = Field(default_factory=list)


# ── ошибки ───────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    loc: Optional[List[str]] = None
    msg: str
    type: str


class ErrorResponse(BaseModel):
    """стандартный формат ошибки."""
    detail: str
