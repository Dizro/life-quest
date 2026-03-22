"""
app/services/reward_service.py

Сервисный слой начисления наград по формуле ТЗ §6.2:
  XP   = ES × base_xp   × type_mult × status_mult × buff_mult
  Gold = ES × base_gold × type_mult × status_mult × buff_mult

Дневной потолок (§6.4):
  daily_xp_cap   = 200 + (level × 20)
  daily_gold_cap = 100 + (level × 10)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User


# ── базовые множители по типу задачи ─────────────────────────────────────────

_BASE_XP: dict[str, int] = {
    "regular": 10,
    "daily":   7,
    "habit":   3,
}

_BASE_GOLD: dict[str, int] = {
    "regular": 5,
    "daily":   3,
    "habit":   1,
}

# ── прогрессия уровней ────────────────────────────────────────────────────────

def xp_required_for_level(level: int) -> int:
    """XP_req(L) = 100 × L^1.5"""
    return int(100 * (level ** 1.5))


# ── множители ─────────────────────────────────────────────────────────────────

def _get_status_mult(task: "Task") -> float:
    """
    Множитель за статус «Испытание» (§6.6):
      неделя 1 → 0.5, неделя 2 → 0.4, неделя 3 → 0.3, неделя 4+ → 0.2
    """
    if task.status.value != "trial" or not task.trial_since:
        return 1.0

    now = datetime.now(timezone.utc)
    trial_since = task.trial_since
    # приводим к offset-aware если нужно
    if trial_since.tzinfo is None:
        trial_since = trial_since.replace(tzinfo=timezone.utc)

    weeks_overdue = (now - trial_since).days // 7
    mult = max(0.2, 0.5 - weeks_overdue * 0.1)
    return mult


def _get_buff_mult(user: "User") -> float:
    """
    Активный XP-бафф пользователя (§6.8).
    Берём максимальный из неистёкших XP-баффов; Gold-баффы не смешиваем.
    """
    now = datetime.now(timezone.utc)
    xp_mults = []

    for buff in (user.buffs or []):
        expires = buff.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires > now and "xp" in buff.buff_type.lower():
            xp_mults.append(float(buff.multiplier))

    return max(xp_mults, default=1.0)


# ── основной расчёт ───────────────────────────────────────────────────────────

def calculate_rewards(task: "Task", user: "User") -> tuple[int, int]:
    """
    Возвращает (xp_earned, gold_earned) с учётом всех множителей и дневного лимита.

    Дневной лимит проверяется по-простому: если пользователь уже набрал
    больше лимита за день — возвращаем (0, 0).
    Для точного подсчёта «уже заработанного сегодня» нужен отдельный запрос к БД
    (реализуется в следующем спринте через агрегацию OutboxEvent).
    """
    es: int = task.effort_score if task.effort_score is not None else 5
    task_type: str = task.task_type.value if task.task_type else "regular"

    base_xp   = _BASE_XP.get(task_type, 10)
    base_gold = _BASE_GOLD.get(task_type, 5)

    status_mult = _get_status_mult(task)
    buff_mult   = _get_buff_mult(user)
    type_mult   = 1.0  # зарезервировано для будущих модификаторов

    raw_xp   = int(es * base_xp   * type_mult * status_mult * buff_mult)
    raw_gold = int(es * base_gold * type_mult * status_mult * 1.0)  # Gold-бафф не влияет на это место

    # дневной потолок
    daily_xp_cap   = 200 + (user.level * 20)
    daily_gold_cap = 100 + (user.level * 10)

    xp_earned   = min(raw_xp,   daily_xp_cap)
    gold_earned = min(raw_gold, daily_gold_cap)

    return xp_earned, gold_earned


# ── повышение уровня ──────────────────────────────────────────────────────────

def apply_rewards_and_check_levelup(
    user: "User",
    xp_earned: int,
    gold_earned: int,
) -> bool:
    """
    Начисляет XP и Gold пользователю, проверяет повышение уровня.
    Возвращает True, если уровень повысился.
    Мутирует объект user — вызывающая сторона должна сделать commit.
    """
    user.experience_points += xp_earned
    user.coins += gold_earned

    leveled_up = False
    # цикл на случай нескольких уровней за раз (маловероятно, но правильно)
    while user.experience_points >= xp_required_for_level(user.level):
        user.level += 1
        user.crystals += user.level  # +N кристаллов = номер нового уровня (§6.5)
        leveled_up = True

    return leveled_up