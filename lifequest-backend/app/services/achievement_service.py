"""
app/services/achievement_service.py

Сервис для проверки и автовыдачи достижений игроку.
Запускается после ключевых действий (выполнение задачи, получение уровня и т.д.).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement
from app.models.user import User
from app.models.user_achievement import UserAchievement
from app.services.reward_service import apply_rewards_and_check_levelup
from app.services.notification_service import send_achievement_notification

async def check_and_grant_achievements(
    session: AsyncSession,
    user: User,
    is_trial_completed: bool = False,
    task_completed: bool = False,
) -> list[str]:
    """
    Проверяет, выполнил ли пользователь условия для достижений,
    которых у него еще нет, и разблокирует их.
    Начисляет xp_bonus за новые достижения.
    Мутирует user в сессии, но НЕ вызывает commit (это делает роутер).
    
    Возвращает список кодов разблокированных сейчас достижений.
    """
    # 1. Получаем список уже разблокированных достижений
    result = await session.execute(
        select(Achievement.code)
        .join(UserAchievement)
        .where(UserAchievement.user_id == user.id)
    )
    unlocked_codes = set(result.scalars().all())
    
    newly_unlocked_codes = []
    
    # 2. Проверяем условия для известных достижений
    if "first_quest_completed" not in unlocked_codes and task_completed:
        newly_unlocked_codes.append("first_quest_completed")
        
    if "streak_3_days" not in unlocked_codes and user.current_streak >= 3:
        newly_unlocked_codes.append("streak_3_days")
        
    if "streak_7_days" not in unlocked_codes and user.current_streak >= 7:
        newly_unlocked_codes.append("streak_7_days")
        
    if "level_5_reached" not in unlocked_codes and user.level >= 5:
        newly_unlocked_codes.append("level_5_reached")
        
    if "first_trial_survived" not in unlocked_codes and is_trial_completed:
        newly_unlocked_codes.append("first_trial_survived")
        
    if not newly_unlocked_codes:
        return []
        
    # 3. Выдаем достижения
    achievements_query = select(Achievement).where(Achievement.code.in_(newly_unlocked_codes))
    ach_result = await session.execute(achievements_query)
    achievements = ach_result.scalars().all()
    
    granted_codes = []
    total_xp_bonus = 0
    for ach in achievements:
        user_ach = UserAchievement(user_id=user.id, achievement_id=ach.id)
        session.add(user_ach)
        total_xp_bonus += ach.xp_bonus
        granted_codes.append(ach.code)
        await send_achievement_notification(user, ach.title, ach.xp_bonus)
        
    # 4. Начисляем бонус (опционально может поднять уровень еще раз)
    if total_xp_bonus > 0:
        apply_rewards_and_check_levelup(user, total_xp_bonus, 0)
        # Если вдруг из-за бонуса он апнул 5 уровень (рекурсивный случай проверки)
        # Идеальным решением было бы рекурсивно проверить достижения, 
        # но мы оставим это на следующее событие апдейта пользователя для простоты.
        
    return granted_codes
