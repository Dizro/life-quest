"""
app/services/achievement_service.py

Сервис для проверки и автовыдачи достижений игроку.
Запускается после ключевых действий (выполнение задачи, получение уровня и т.д.).
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement
from app.models.user import User
from app.models.task import Task
from app.models.user_achievement import UserAchievement
from app.services.reward_service import apply_rewards_and_check_levelup
from app.services.notification_service import send_achievement_notification


async def check_and_grant_achievements(
    session: AsyncSession,
    user: User,
    is_trial_completed: bool = False,
    task_completed: bool = False,
    purchase_made: bool = False,
    subtask_parent_completed: bool = False,
    redeemed_count: int = 0,
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

    # 2. Получаем статистику пользователя (агрегаты)
    total_completed = await session.scalar(
        select(func.count(Task.id)).where(
            Task.owner_id == user.id,
            Task.status == "completed"
        )
    ) or 0

    total_gold_earned = await session.scalar(
        select(func.sum(Task.coin_reward)).where(
            Task.owner_id == user.id,
            Task.status == "completed"
        )
    ) or 0

    # 3. Количество выкупов испытаний (если не передано явно)
    if redeemed_count == 0 and "redeem_3_trials" not in unlocked_codes:
        redeemed_count = await session.scalar(
            select(func.count(Task.id)).where(
                Task.owner_id == user.id,
                Task.status == "redeemed"
            )
        ) or 0

    newly_unlocked_codes = []

    # 4. Проверяем условия для каждого достижения
    # --- Существующие достижения ---
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

    # --- Новые достижения (по ТЗ) ---
    if "streak_30_days" not in unlocked_codes and user.current_streak >= 30:
        newly_unlocked_codes.append("streak_30_days")

    if "quests_10_completed" not in unlocked_codes and total_completed >= 10:
        newly_unlocked_codes.append("quests_10_completed")

    if "quests_100_completed" not in unlocked_codes and total_completed >= 100:
        newly_unlocked_codes.append("quests_100_completed")

    if "quests_1000_completed" not in unlocked_codes and total_completed >= 1000:
        newly_unlocked_codes.append("quests_1000_completed")

    if "gold_1000_earned" not in unlocked_codes and total_gold_earned >= 1000:
        newly_unlocked_codes.append("gold_1000_earned")

    if "crystals_50_earned" not in unlocked_codes and user.crystals >= 50:
        newly_unlocked_codes.append("crystals_50_earned")

    if "first_purchase" not in unlocked_codes and purchase_made:
        newly_unlocked_codes.append("first_purchase")

    # Достижение "epic_gold_spent" требует поля total_gold_spent в User.
    # В текущей версии модели такого поля нет, поэтому пока отключено.
    # Для активации нужно добавить поле и миграцию.
    # if "epic_gold_spent" not in unlocked_codes and (user.total_gold_spent or 0) >= 500:
    #     newly_unlocked_codes.append("epic_gold_spent")

    if "all_subtasks_complete" not in unlocked_codes and subtask_parent_completed:
        newly_unlocked_codes.append("all_subtasks_complete")

    if "redeem_3_trials" not in unlocked_codes and redeemed_count >= 3:
        newly_unlocked_codes.append("redeem_3_trials")

    if not newly_unlocked_codes:
        return []

    # 5. Выдаём достижения
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
        # Отправляем push‑уведомление о достижении
        await send_achievement_notification(user, ach.title, ach.xp_bonus)

    # 6. Начисляем бонус (может повысить уровень)
    if total_xp_bonus > 0:
        apply_rewards_and_check_levelup(user, total_xp_bonus, 0)
        # Повторная проверка достижений не требуется – новые уровни обработаются
        # при следующем вызове (например, при следующем выполнении задачи)

    return granted_codes