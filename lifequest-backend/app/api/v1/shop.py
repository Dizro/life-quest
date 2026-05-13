"""
Магазин (FR-6).
Покупка предметов за золото/кристаллы, добавление в инвентарь.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.inventory import UserInventory

router = APIRouter(prefix="/shop", tags=["shop"])

# Каталог предметов магазина (серверная правда)
SHOP_CATALOG = {
    "hat_adv": {"name": "Шляпа авантюриста", "type": "hat", "gold": 50, "crystals": 0},
    "cloak_traveler": {"name": "Плащ путника", "type": "armor", "gold": 120, "crystals": 0},
    "armor_hero": {"name": "Доспехи героя", "type": "armor", "gold": 300, "crystals": 0},
    "buff_gold": {"name": "Победный дух", "type": "buff", "gold": 50, "crystals": 0},
    "theme_night": {"name": "Тема «Ночь»", "type": "buff", "gold": 200, "crystals": 0},
    "pet_slime": {"name": "Слизень", "type": "pet", "gold": 0, "crystals": 5},
    "pet_phoenix": {"name": "Феникс", "type": "pet", "gold": 0, "crystals": 25},
    "pet_dragon": {"name": "Дракончик", "type": "pet", "gold": 0, "crystals": 50},
}


class BuyRequest(BaseModel):
    item_id: str


class BuyResponse(BaseModel):
    success: bool
    message: str
    gold: int
    crystals: int


@router.post("/buy", response_model=BuyResponse)
async def buy_item(
    body: BuyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Покупка предмета из магазина."""
    item_def = SHOP_CATALOG.get(body.item_id)
    if not item_def:
        raise HTTPException(status_code=404, detail="Предмет не найден в каталоге")

    # Проверка: уже куплен?
    existing = await db.execute(
        select(UserInventory).where(
            UserInventory.user_id == current_user.id,
            UserInventory.item_key == body.item_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Этот предмет уже есть в инвентаре")

    # Проверка средств
    if item_def["gold"] > 0 and current_user.gold < item_def["gold"]:
        raise HTTPException(status_code=400, detail="Недостаточно золота")
    if item_def["crystals"] > 0 and current_user.crystals < item_def["crystals"]:
        raise HTTPException(status_code=400, detail="Недостаточно кристаллов")

    # Списание
    current_user.gold -= item_def["gold"]
    current_user.crystals -= item_def["crystals"]

    # Добавление в инвентарь
    inv_item = UserInventory(
        user_id=current_user.id,
        item_key=body.item_id,
        item_type=item_def["type"],
        item_name=item_def["name"],
        is_equipped=False,
    )
    db.add(inv_item)
    await db.commit()

    return BuyResponse(
        success=True,
        message=f"Вы купили: {item_def['name']}!",
        gold=current_user.gold,
        crystals=current_user.crystals,
    )
