from pydantic import BaseModel, Field
from typing import Optional


class ProfileSettingsUpdate(BaseModel):
    theme: Optional[str] = Field(None, pattern="^(dark|light)$")
    notifications_deadlines: Optional[bool] = None
    notifications_evening: Optional[bool] = None
    notifications_achievements: Optional[bool] = None
    language: Optional[str] = Field(None, pattern="^(ru|en)$")


class ProfileSettingsResponse(BaseModel):
    theme: str
    notifications_deadlines: bool
    notifications_evening: bool
    notifications_achievements: bool
    language: str

    model_config = {"from_attributes": True}