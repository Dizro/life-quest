from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.achievement import AchievementsListResponse
from app.services.achievement_service import get_user_achievements

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get("/", response_model=AchievementsListResponse)
async def list_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    SCRUM-203: Отдаёт список всех достижений (разблокированные + заблокированные)
    с прогрессом для конкретного пользователя.
    """
    data = await get_user_achievements(current_user.id, db)
    return AchievementsListResponse(**data)