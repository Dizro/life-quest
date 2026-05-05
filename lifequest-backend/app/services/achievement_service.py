from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.achievement import Achievement, UserAchievement
from app.models.task import Task
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


async def check_and_unlock_achievements(
    user: User, db: AsyncSession
) -> List[Achievement]:
    """
    Проверяет все условия и выдаёт новые ачивки.
    Возвращает список разблокированных достижений.
    """
    # Считаем текущую статистику
    tasks_count_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.user_id == user.id,
            Task.status == "completed"
        )
    )
    tasks_completed = tasks_count_result.scalar() or 0

    # Уже разблокированные достижения
    unlocked_result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)
    )
    already_unlocked = {row[0] for row in unlocked_result.fetchall()}

    # Все активные достижения
    all_ach_result = await db.execute(
        select(Achievement).where(Achievement.is_active == True)
    )
    all_achievements = all_ach_result.scalars().all()

    newly_unlocked = []
    for ach in all_achievements:
        if ach.id in already_unlocked:
            continue

        unlocked = False
        if ach.condition_type == "tasks_count" and tasks_completed >= ach.condition_value:
            unlocked = True
        elif ach.condition_type == "streak_days" and user.streak_days >= ach.condition_value:
            unlocked = True
        elif ach.condition_type == "xp_total" and user.xp >= ach.condition_value:
            unlocked = True
        elif ach.condition_type == "level" and user.level >= ach.condition_value:
            unlocked = True

        if unlocked:
            ua = UserAchievement(user_id=user.id, achievement_id=ach.id)
            db.add(ua)
            # Выдаём награду
            user.crystals += ach.crystal_reward
            user.xp += ach.xp_reward
            newly_unlocked.append(ach)
            logger.info("Achievement unlocked: %s for user %s", ach.key, user.id)

    if newly_unlocked:
        await db.flush()

    return newly_unlocked


async def get_user_achievements(
    user_id: int, db: AsyncSession
) -> dict:
    """SCRUM-203: Отдаёт список всех достижений с флагом разблокировки."""
    all_ach = await db.execute(select(Achievement).where(Achievement.is_active == True))
    all_achievements = all_ach.scalars().all()

    unlocked_result = await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user_id)
    )
    unlocked_map = {
        ua.achievement_id: ua.unlocked_at
        for ua in unlocked_result.scalars().all()
    }

    # Считаем прогресс пользователя
    tasks_count_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.user_id == user_id, Task.status == "completed"
        )
    )
    tasks_completed = tasks_count_result.scalar() or 0

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one()

    unlocked_list = []
    locked_list = []

    for ach in all_achievements:
        is_unlocked = ach.id in unlocked_map

        # Вычисляем прогресс
        current_value = 0
        if ach.condition_type == "tasks_count":
            current_value = tasks_completed
        elif ach.condition_type == "streak_days":
            current_value = user.streak_days
        elif ach.condition_type == "level":
            current_value = user.level

        progress = min(1.0, current_value / ach.condition_value) if ach.condition_value > 0 else 0.0

        item = {
            "id": ach.id,
            "key": ach.key,
            "name": ach.name,
            "description": ach.description,
            "icon": ach.icon,
            "crystal_reward": ach.crystal_reward,
            "xp_reward": ach.xp_reward,
            "condition_type": ach.condition_type,
            "condition_value": ach.condition_value,
            "unlocked": is_unlocked,
            "unlocked_at": unlocked_map.get(ach.id),
            "progress": progress if not is_unlocked else 1.0,
        }

        if is_unlocked:
            unlocked_list.append(item)
        else:
            locked_list.append(item)

    return {
        "unlocked": unlocked_list,
        "locked": locked_list,
        "total_unlocked": len(unlocked_list),
        "total": len(all_achievements),
    }