"""
Сервис расчёта наград — единственный источник истины для формул.

Формулы (раздел 6.2 ТЗ):
  XP   = ES × base_xp   × type_mult × status_mult × buff_mult
  Gold = ES × base_gold  × type_mult × status_mult × buff_mult

Прогрессия уровней (6.3):  XP_req(L) = 100 × L^1.5
Дневной потолок (6.4):     XP = 200 + level×20,  Gold = 100 + level×10
Привычки (6.4):            отдельный лимит 30 XP, 15 Gold
Кристаллы при левел-апе:   +N кристаллов (N = новый уровень)
"""
import math
from typing import Tuple
from app.models.user import User
from app.models.task import Task
from datetime import datetime, timezone

# ── Базовые константы (раздел 6.2) ────────────────────────────────────────
BASE_XP = {
    "regular": 10,
    "daily":    7,
    "habit":    3,
    "subtask":  5,
}
BASE_GOLD = {
    "regular": 5,
    "daily":   3,
    "habit":   1,
    "subtask": 3,
}
TYPE_MULT = {
    "regular": 1.0,
    "daily":   1.0,
    "habit":   1.0,
    "subtask": 0.7,
}

# ── Дневные лимиты (раздел 6.4) ──────────────────────────────────────────
DAILY_XP_CAP_BASE   = 200   # + level×20
DAILY_GOLD_CAP_BASE = 100   # + level×10
HABIT_DAILY_XP_CAP  = 30
HABIT_DAILY_GOLD_CAP = 15


def get_status_mult(task: Task) -> float:
    """
    Множитель награды для испытания (раздел 6.6 ТЗ).
    0–6 дней  → 0.5
    7–13 дней → 0.5
    14–20     → 0.4
    21–27     → 0.3
    28+       → 0.2 (минимум)
    Для обычных задач → 1.0
    """
    if task.status != "trial":
        return 1.0
    if not task.trial_expires_at:
        return 0.5
    # trial_expires_at используется как trial_started_at
    days = (datetime.now(timezone.utc) - task.trial_expires_at).days
    if days < 0:
        days = 0
    weeks = days // 7
    if weeks <= 1:
        return 0.5
    if weeks == 2:
        return 0.4
    if weeks == 3:
        return 0.3
    return 0.2


def calculate_rewards(
    effort_score: int,
    task_type: str = "regular",
    status_mult: float = 1.0,
) -> Tuple[int, int]:
    """Возвращает (xp, gold) по ES с учётом type_mult и status_mult."""
    bxp = BASE_XP.get(task_type, 10)
    bgold = BASE_GOLD.get(task_type, 5)
    tmult = TYPE_MULT.get(task_type, 1.0)

    xp = int(effort_score * bxp * tmult * status_mult)
    gold = int(effort_score * bgold * tmult * status_mult)
    return xp, gold


def _reset_daily_if_needed(user: User, now: datetime) -> None:
    """Сбрасывает дневные счётчики если дата сменилась."""
    if user.daily_xp_reset_date is None or user.daily_xp_reset_date.date() < now.date():
        user.daily_xp_earned = 0
        user.daily_gold_earned = 0
        user.daily_xp_reset_date = now


def apply_xp(
    user: User,
    raw_xp: int,
    is_habit: bool = False,
) -> Tuple[int, bool]:
    """
    Применяет XP к игроку с учётом:
    - ежедневного лимита (200 + level×20)
    - множителя XP-баффа
    - формулы уровней XP_req(L) = 100 × L^1.5
    - начисление кристаллов при левел-апе (+N, N=новый уровень)
    Возвращает (actual_xp_gained, leveled_up).
    """
    now = datetime.now(timezone.utc)
    _reset_daily_if_needed(user, now)

    daily_cap = DAILY_XP_CAP_BASE + user.level * 20
    available = daily_cap - user.daily_xp_earned
    if available <= 0:
        return 0, False

    # XP-бафф
    if user.xp_multiplier and user.xp_multiplier > 1.0:
        if user.xp_multiplier_expires and user.xp_multiplier_expires > now:
            raw_xp = int(raw_xp * user.xp_multiplier)

    actual_xp = min(raw_xp, available)
    user.xp += actual_xp
    user.daily_xp_earned += actual_xp
    user.weekly_xp = (user.weekly_xp or 0) + actual_xp

    leveled_up = False
    while user.xp >= user.xp_to_next_level:
        user.xp -= user.xp_to_next_level
        user.level += 1
        # FR-5.9: кристаллы = номер нового уровня
        user.crystals += user.level
        # Формула 6.3: XP_req(L) = 100 × L^1.5
        user.xp_to_next_level = int(100 * math.pow(user.level, 1.5))
        leveled_up = True

    return actual_xp, leveled_up


def apply_gold(
    user: User,
    raw_gold: int,
) -> int:
    """
    Применяет Gold к игроку с учётом дневного лимита (100 + level×10).
    Возвращает фактически начисленное золото.
    """
    now = datetime.now(timezone.utc)
    _reset_daily_if_needed(user, now)

    daily_gold_cap = DAILY_GOLD_CAP_BASE + user.level * 10
    avail = max(0, daily_gold_cap - user.daily_gold_earned)
    actual_gold = min(raw_gold, avail)
    user.gold += actual_gold
    user.daily_gold_earned += actual_gold
    return actual_gold


# ── Привычки: +/− тики ──────────────────────────────────────────────────

def calc_habit_tick(effort_score: int) -> Tuple[int, int]:
    """
    Награда за один + тик привычки (раздел 6.4).
    XP  = max(1, round(ES × 0.6))   → ES=1→1, ES=3→2, ES=5→3, ES=7→4, ES=10→6
    Gold = max(1, round(ES × 0.25))  → ES=1→1, ES=3→1, ES=5→1, ES=7→2, ES=10→3
    Маленькие, но приятные тики. Дневной лимит: 30 XP, 15 Gold.
    """
    xp = max(1, round(effort_score * 0.6))
    gold = max(1, round(effort_score * 0.25))
    return xp, gold


def apply_habit_plus(user: User, effort_score: int) -> Tuple[int, int, bool]:
    """
    Применяет + тик привычки.
    Лимиты привычек (раздел 6.4): 30 XP/день, 15 Gold/день.
    Также учитывает общий дневной XP/Gold лимит.
    Возвращает (xp_gained, gold_gained, leveled_up).
    """
    now = datetime.now(timezone.utc)
    _reset_daily_if_needed(user, now)

    tick_xp, tick_gold = calc_habit_tick(effort_score)

    # Общий дневной лимит XP (200 + level×20)
    daily_xp_cap = DAILY_XP_CAP_BASE + user.level * 20
    avail_xp = max(0, daily_xp_cap - user.daily_xp_earned)
    actual_xp = min(tick_xp, avail_xp)

    # Общий дневной лимит Gold (100 + level×10)
    daily_gold_cap = DAILY_GOLD_CAP_BASE + user.level * 10
    avail_gold = max(0, daily_gold_cap - user.daily_gold_earned)
    actual_gold = min(tick_gold, avail_gold)

    # XP-бафф
    if user.xp_multiplier and user.xp_multiplier > 1.0:
        if user.xp_multiplier_expires and user.xp_multiplier_expires > now:
            actual_xp = int(actual_xp * user.xp_multiplier)

    user.xp += actual_xp
    user.gold += actual_gold
    user.daily_xp_earned += actual_xp
    user.daily_gold_earned += actual_gold
    user.weekly_xp = (user.weekly_xp or 0) + actual_xp

    leveled_up = False
    while user.xp >= user.xp_to_next_level:
        user.xp -= user.xp_to_next_level
        user.level += 1
        user.crystals += user.level
        user.xp_to_next_level = int(100 * math.pow(user.level, 1.5))
        leveled_up = True

    return actual_xp, actual_gold, leveled_up


def apply_habit_minus(user: User, effort_score: int) -> Tuple[int, int]:
    """
    Применяет − тик привычки. Отнимает награду за 1 тик.
    XP и Gold не могут стать < 0.
    Возвращает (xp_lost, gold_lost).
    """
    tick_xp, tick_gold = calc_habit_tick(effort_score)
    xp_lost = min(tick_xp, user.xp)
    gold_lost = min(tick_gold, user.gold)
    user.xp -= xp_lost
    user.gold -= gold_lost
    return xp_lost, gold_lost


FARRIX_PHRASES_WITH_TASK = [
    "«{task}» — выполнено! Отличная работа, {name}. Каждый шаг приближает тебя к легенде.",
    "{name}, ты завершил «{task}»! Ещё одна победа в твоей книге подвигов.",
    "Квест «{task}» — закрыт! Твоя дисциплина внушает уважение, {name}.",
    "«{task}» позади. Превосходно! Не останавливайся, {name} — стрик зовёт!",
    "Вижу, «{task}» больше не проблема. Ты растёшь, {name}!",
    "{name} одолел «{task}»! Враги дрожат, награды капают.",
    "Задание «{task}» сдано. Так держать, {name} — ты на верном пути.",
    "«{task}»? Готово! {name}, Фаррикс ставит тебе зачёт с отличием.",
    "Ещё один квест в копилку — «{task}». {name}, ты машина!",
    "{name}, «{task}» выполнено блестяще. Магия дисциплины — сильнейшее заклинание.",
]

FARRIX_PHRASES_HARD = [
    "Это был настоящий подвиг — «{task}»! Такие задачи закаляют героев, {name}.",
    "{name}, ты взял «{task}» — задачу уровня босса! Фаррикс аплодирует стоя.",
    "«{task}» — серьёзный вызов, но ты справился. Уважение, {name}.",
    "Немногие решились бы на «{task}». Ты не из робкого десятка, {name}!",
]

def get_farrix_phrase(
    effort_score: int,
    leveled_up: bool,
    user_name: str = "искатель",
    task_title: str = "",
) -> str:
    import random
    task = task_title[:60] if task_title else "задание"
    if leveled_up:
        return f"🎉 УРОВЕНЬ ВВЕРХ! «{task}» стал решающим — ты становишься сильнее с каждым днём, {user_name}!"
    if effort_score >= 10:
        return random.choice(FARRIX_PHRASES_HARD).format(name=user_name, task=task)
    return random.choice(FARRIX_PHRASES_WITH_TASK).format(name=user_name, task=task)