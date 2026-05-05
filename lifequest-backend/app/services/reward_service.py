from typing import Tuple
from app.models.user import User
from app.models.task import Task
from datetime import datetime, timezone


XP_PER_EFFORT_POINT = 10
GOLD_PER_EFFORT_POINT = 4
DAILY_XP_CAP_BASE = 200
HABIT_DAILY_XP_CAP = 30


def calculate_rewards(effort_score: int, task_type: str = "regular") -> Tuple[int, int]:
    """Возвращает (xp, gold) по effort score."""
    xp = effort_score * XP_PER_EFFORT_POINT
    gold = effort_score * GOLD_PER_EFFORT_POINT
    if task_type == "habit":
        xp = min(xp, HABIT_DAILY_XP_CAP)
    return xp, gold


def apply_xp(user: User, raw_xp: int) -> Tuple[int, bool]:
    """
    Применяет XP к игроку с учётом:
    - ежедневного лимита
    - множителя баффа
    Возвращает (actual_xp_gained, leveled_up).
    """
    now = datetime.now(timezone.utc)

    # Сброс дневного счётчика
    if user.daily_xp_reset_date is None or user.daily_xp_reset_date.date() < now.date():
        user.daily_xp_earned = 0
        user.daily_xp_reset_date = now

    daily_cap = DAILY_XP_CAP_BASE + user.level * 20
    available = daily_cap - user.daily_xp_earned
    if available <= 0:
        return 0, False

    # Бафф множитель
    if user.xp_multiplier_expires and user.xp_multiplier_expires > now:
        raw_xp = int(raw_xp * user.xp_multiplier)

    actual_xp = min(raw_xp, available)
    user.xp += actual_xp
    user.daily_xp_earned += actual_xp

    leveled_up = False
    while user.xp >= user.xp_to_next_level:
        user.xp -= user.xp_to_next_level
        user.level += 1
        user.xp_to_next_level = int(user.xp_to_next_level * 1.5)
        leveled_up = True

    return actual_xp, leveled_up


FARRIX_PHRASES = [
    "Отличная работа, {name}! Каждый шаг приближает тебя к легенде.",
    "Ещё одна победа! Ты растёшь быстрее, чем я ожидал, {name}.",
    "Задача выполнена. Твоя дисциплина внушает уважение.",
    "Превосходно! Стрик продолжается — не останавливайся, {name}.",
    "Квест завершён. Фаррикс доволен твоим прогрессом."
]

def get_farrix_phrase(effort_score: int, leveled_up: bool, user_name: str = "искатель") -> str:
    if leveled_up:
        return f"🎉 УРОВЕНЬ ВВЕРХ! Ты становишься сильнее с каждым днём, {user_name}!"
    if effort_score >= 15:
        return f"Это был настоящий подвиг, {user_name}! Такие задачи закаляют героев."
    if effort_score >= 10:
        return f"Серьёзная работа позади. Ты справился — Фаррикс горд тобой, {user_name}."
    import random
    return random.choice(FARRIX_PHRASES).format(name=user_name)