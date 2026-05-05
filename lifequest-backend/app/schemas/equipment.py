from pydantic import BaseModel
from typing import Optional


class EquipItemRequest(BaseModel):
    item_key: str
    slot: str  # hat | armor | weapon | pet | background


class EquipItemResponse(BaseModel):
    slot: str
    item_key: Optional[str]
    success: bool
    message: str


class InventoryItemResponse(BaseModel):
    id: int
    item_key: str
    item_type: str
    item_name: str
    is_equipped: bool

    model_config = {"from_attributes": True}


class InventoryResponse(BaseModel):
    items: list[InventoryItemResponse]
    equipped: dict  # {slot: item_key}