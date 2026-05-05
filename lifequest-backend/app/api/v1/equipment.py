from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.inventory import UserInventory
from app.schemas.equipment import EquipItemRequest, EquipItemResponse, InventoryResponse

router = APIRouter(prefix="/equipment", tags=["equipment"])

VALID_SLOTS = {"hat", "armor", "weapon", "pet", "background"}
SLOT_TO_FIELD = {
    "hat": "equipped_hat",
    "armor": "equipped_armor",
    "weapon": "equipped_weapon",
    "pet": "equipped_pet",
    "background": "equipped_background",
}


@router.get("/inventory", response_model=InventoryResponse)
async def get_inventory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """SCRUM-205: Список всего инвентаря игрока с пометкой экипированных предметов."""
    result = await db.execute(
        select(UserInventory).where(UserInventory.user_id == current_user.id)
    )
    items = result.scalars().all()

    equipped = {
        "hat": current_user.equipped_hat,
        "armor": current_user.equipped_armor,
        "weapon": current_user.equipped_weapon,
        "pet": current_user.equipped_pet,
        "background": current_user.equipped_background,
    }

    return InventoryResponse(
        items=[
            {
                "id": item.id,
                "item_key": item.item_key,
                "item_type": item.item_type,
                "item_name": item.item_name,
                "is_equipped": item.is_equipped,
            }
            for item in items
        ],
        equipped=equipped,
    )


@router.post("/equip", response_model=EquipItemResponse)
async def equip_item(
    data: EquipItemRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """SCRUM-205: Смена надетого предмета и сохранение состояния в профиле."""
    if data.slot not in VALID_SLOTS:
        raise HTTPException(status_code=400, detail=f"Неверный слот. Допустимые: {VALID_SLOTS}")

    # Проверяем, есть ли предмет в инвентаре
    inv_result = await db.execute(
        select(UserInventory).where(
            UserInventory.user_id == current_user.id,
            UserInventory.item_key == data.item_key,
        )
    )
    item = inv_result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Предмет не найден в инвентаре")

    # Снимаем предыдущий предмет из этого слота
    prev_key = getattr(current_user, SLOT_TO_FIELD[data.slot])
    if prev_key:
        prev_result = await db.execute(
            select(UserInventory).where(
                UserInventory.user_id == current_user.id,
                UserInventory.item_key == prev_key,
            )
        )
        prev_item = prev_result.scalar_one_or_none()
        if prev_item:
            prev_item.is_equipped = False

    # Экипируем новый предмет
    item.is_equipped = True
    setattr(current_user, SLOT_TO_FIELD[data.slot], data.item_key)

    await db.commit()

    return EquipItemResponse(
        slot=data.slot,
        item_key=data.item_key,
        success=True,
        message=f"Предмет '{item.item_name}' экипирован в слот '{data.slot}'",
    )


@router.post("/unequip/{slot}", response_model=EquipItemResponse)
async def unequip_slot(
    slot: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Снять предмет из слота."""
    if slot not in VALID_SLOTS:
        raise HTTPException(status_code=400, detail="Неверный слот")

    current_key = getattr(current_user, SLOT_TO_FIELD[slot])
    if current_key:
        inv_result = await db.execute(
            select(UserInventory).where(
                UserInventory.user_id == current_user.id,
                UserInventory.item_key == current_key,
            )
        )
        item = inv_result.scalar_one_or_none()
        if item:
            item.is_equipped = False

    setattr(current_user, SLOT_TO_FIELD[slot], None)
    await db.commit()

    return EquipItemResponse(slot=slot, item_key=None, success=True, message="Предмет снят")