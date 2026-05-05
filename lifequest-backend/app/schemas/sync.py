from pydantic import BaseModel, Field
from typing import List, Optional, Any, Literal
from datetime import datetime


class OfflineAction(BaseModel):
    action_type: Literal["CREATE_TASK", "COMPLETE_TASK", "UPDATE_TASK", "DELETE_TASK"]
    client_task_id: str = Field(..., description="Клиентский UUID задачи")
    timestamp: datetime = Field(..., description="Время действия на клиенте")
    payload: dict = Field(default_factory=dict)


class SyncRequest(BaseModel):
    actions: List[OfflineAction] = Field(..., max_length=500, description="Список действий офлайн")
    last_sync_at: Optional[datetime] = None


class SyncActionResult(BaseModel):
    client_task_id: str
    action_type: str
    success: bool
    server_task_id: Optional[int] = None
    conflict: bool = False
    conflict_reason: Optional[str] = None
    error: Optional[str] = None


class SyncResponse(BaseModel):
    processed: int
    succeeded: int
    failed: int
    conflicts: int
    results: List[SyncActionResult]
    server_time: datetime