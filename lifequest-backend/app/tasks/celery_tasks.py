"""
Фоновые Celery-задачи.

ИЗМЕНЕНИЯ vs оригинал:
  - Добавлена задача reset_weekly_xp — сбрасывает weekly_xp каждый понедельник (FR-7.3)
  - Все tasks.py и sync.py импортируют get_current_user из app.api.dependencies (единая реализация)
  - В beat_schedule добавлен reset-weekly-xp по крону каждый понедельник 00:01
  - _async_reset_streaks: исправлено сравнение дат (timezone-aware)
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


# ── process_effort_score ──────────────────────────────────────────────────────

@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_effort_score(self, task_id: int) -> None:
    """
    Фоновая ИИ-оценка сложности задачи (FR-3.1).
    Работает асинхронно — фронтенд не ждёт.
    Контракт для фронтенда: когда статус меняется с pending_es → active,
    поля effort_score и xp_reward/gold_reward заполнены.
    """
    try:
        asyncio.run(_async_process_effort_score(task_id))
    except Exception as exc:
        logger.error("process_effort_score failed for task %s: %s", task_id, exc)
        raise self.retry(exc=exc)


async def _async_process_effort_score(task_id: int) -> None:
    from sqlalchemy import select
    from app.core.database import async_session_factory
    from app.models.task import Task
    from app.services.ai_service import get_effort_score
    from app.services.reward_service import calculate_rewards

    async with async_session_factory() as db:
        try:
            result = await db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()

            if not task or task.status not in ("pending_es", "active"):
                logger.warning("Task %s not found or invalid status", task_id)
                return

            ai_response = await get_effort_score(task.title)
            es = ai_response.effort_score

            task.effort_score = es.value
            task.effort_confidence = es.confidence
            task.effort_reasoning = es.reasoning
            task.complexity_level = es.complexity_level.value
            # es_ready = True позволяет фронтенду остановить поллинг
            task.status = "active"

            xp, gold = calculate_rewards(es.value, task.task_type)
            task.xp_reward = xp
            task.gold_reward = gold

            await db.commit()
            logger.info("ES assigned: task=%s score=%s", task_id, es.value)

        except Exception as e:
            await db.rollback()
            logger.error("Error in _async_process_effort_score: %s", e)
            raise


# ── reset_broken_streaks ──────────────────────────────────────────────────────

@celery_app.task
def reset_broken_streaks() -> None:
    """
    Сбрасывает стрики у игроков, пропустивших день активности.
    Запуск: 00:05 UTC ежедневно.
    """
    asyncio.run(_async_reset_streaks())


async def _async_reset_streaks() -> None:
    from sqlalchemy import select
    from app.core.database import async_session_factory
    from app.models.user import User

    async with async_session_factory() as db:
        # Пропустил день = last_activity_date < начало вчерашнего дня UTC
        now = datetime.now(timezone.utc)
        yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        result = await db.execute(
            select(User).where(
                User.streak_days > 0,
                User.last_activity_date < yesterday_start,
            )
        )
        users = result.scalars().all()

        for user in users:
            user.streak_days = 0
            logger.info("Streak reset for user %s", user.id)

        if users:
            await db.commit()
            logger.info("Reset streaks for %s users", len(users))


# ── transition_overdue_tasks_to_trial ────────────────────────────────────────

@celery_app.task
def transition_overdue_tasks_to_trial() -> None:
    """
    Переводит просроченные задачи в статус 'trial' (Испытание).
    Запуск: каждые 10 минут.
    """
    asyncio.run(_async_transition_overdue())


async def _async_transition_overdue() -> None:
    from sqlalchemy import select
    from app.core.database import async_session_factory
    from app.models.task import Task

    async with async_session_factory() as db:
        now = datetime.now(timezone.utc)
        # Только regular и daily (привычки не становятся испытаниями — мини-ТЗ)
        result = await db.execute(
            select(Task).where(
                Task.status == "active",
                Task.deadline < now,
                Task.deadline.isnot(None),
                Task.task_type.in_(["regular", "daily"]),
            )
        )
        tasks = result.scalars().all()

        for task in tasks:
            task.status = "trial"
            # trial_expires_at хранит дату перехода в испытание (trial_started_at)
            task.trial_expires_at = now
            # Стоимость выкупа = ES × 10 (мини-ТЗ)
            task.redeem_cost = (task.effort_score or 5) * 10

        if tasks:
            await db.commit()
            logger.info("Transitioned %s tasks to trial", len(tasks))


# ── reset_weekly_xp ──────────────────────────────────────────────────────────

@celery_app.task
def reset_weekly_xp() -> None:
    """
    Сбрасывает weekly_xp у всех пользователей каждый понедельник.
    Необходимо для корректной работы недельного лидерборда (FR-7.3).
    Также сбрасывает Redis-кэш лидерборда.
    """
    asyncio.run(_async_reset_weekly_xp())


async def _async_reset_weekly_xp() -> None:
    from sqlalchemy import update
    from app.core.database import async_session_factory
    from app.models.user import User
    import redis.asyncio as aioredis

    async with async_session_factory() as db:
        await db.execute(update(User).values(weekly_xp=0))
        await db.commit()
        logger.info("Weekly XP reset for all users")

    # Инвалидируем кэш лидерборда
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        keys = await r.keys("lb:weekly_xp:*")
        if keys:
            await r.delete(*keys)
        await r.aclose()
        logger.info("Leaderboard cache invalidated after weekly_xp reset")
    except Exception as e:
        logger.warning("Could not invalidate leaderboard cache: %s", e)


# ── Обновление beat_schedule ─────────────────────────────────────────────────
# ВНИМАНИЕ: beat_schedule определяется в celery_app.py.
# Добавьте в celery_app.py следующую запись:
#
#   "reset-weekly-xp": {
#       "task": "app.tasks.celery_tasks.reset_weekly_xp",
#       "schedule": crontab(hour=0, minute=1, day_of_week=1),  # Пн 00:01 UTC
#       "options": {"expires": 3600},
#   },
#
# Для использования crontab: from celery.schedules import crontab