"""
app/tasks/celery_tasks.py

Celery-задачи для асинхронной обработки:
- Оценка Effort Score (YandexGPT)
- Перевод просроченных задач в испытания
- Сброс стриков
- Проверка дедлайнов для уведомлений
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.task import Task
from app.models.user import User
from app.services.ai_service import evaluate_effort_score
from app.services.notification_service import send_task_deadline_reminder

logger = logging.getLogger(__name__)


# ========== Существующие задачи ==========

@celery_app.task(
    name="tasks.evaluate_es",
    bind=True,
    max_retries=2,
    default_retry_delay=5,
    acks_late=True,
)
def evaluate_es_task(self, task_id: str, task_title: str) -> dict:
    """Запрашивает Effort Score у YandexGPT и сохраняет в БД."""
    try:
        result = asyncio.run(_evaluate_and_save(task_id, task_title))
        return result
    except Exception as exc:
        logger.error("Celery task evaluate_es failed for %s: %s", task_id, exc)
        raise self.retry(exc=exc)


async def _evaluate_and_save(task_id: str, task_title: str) -> dict:
    """Асинхронно оценивает ES и обновляет задачу в БД."""
    es, reason = await evaluate_effort_score(task_title)
    
    async with async_session_factory() as session:
        result = await session.execute(
            select(Task).where(Task.id == uuid.UUID(task_id))
        )
        task = result.scalar_one_or_none()
        
        if not task:
            logger.warning("Task %s not found — skipping ES update", task_id)
            return {"task_id": task_id, "effort_score": None, "reason": "task not found"}
        
        task.effort_score = es
        if task.status.value == "pending_es":
            task.status = "active"
        
        session.add(task)
        await session.commit()
        
        logger.info("✅ ES updated: task=%s, score=%d, reason=%s", task_id, es, reason)
    
    return {"task_id": task_id, "effort_score": es, "reason": reason}


@celery_app.task(name="tasks.transition_overdue_tasks_to_trial")
def transition_overdue_tasks_to_trial():
    """Cron-задача (00:01 ежедневно). Переводит просроченные задачи в статус 'trial'."""
    try:
        count = asyncio.run(_transition_overdue_tasks_to_trial_async())
        return {"processed": count}
    except Exception as exc:
        logger.error("Celery task transition_overdue_tasks_to_trial failed: %s", exc)
        raise


async def _transition_overdue_tasks_to_trial_async() -> int:
    now_utc = datetime.now(timezone.utc)
    
    async with async_session_factory() as session:
        query = select(Task).where(
            Task.status == "active",
            Task.due_date != None,
            Task.due_date < now_utc,
            Task.task_type.in_(["regular", "daily"])
        )
        result = await session.execute(query)
        tasks = result.scalars().all()
        
        count = len(tasks)
        for t in tasks:
            t.status = "trial"
            t.trial_since = now_utc
        
        if count > 0:
            await session.commit()
            logger.info("✅ Transitioned %d overdue tasks to 'trial' status", count)
    
    return count


@celery_app.task(name="tasks.reset_broken_streaks")
def reset_broken_streaks():
    """Cron-задача (00:05 ежедневно). Сбрасывает стрики неактивных пользователей."""
    try:
        count = asyncio.run(_reset_broken_streaks_async())
        return {"reset_count": count}
    except Exception as exc:
        logger.error("Celery task reset_broken_streaks failed: %s", exc)
        raise


async def _reset_broken_streaks_async() -> int:
    now_utc = datetime.now(timezone.utc)
    today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    
    async with async_session_factory() as session:
        subq = select(Task.owner_id).where(
            Task.task_type == "daily",
            Task.status == "completed",
            Task.completed_at >= yesterday_start,
            Task.completed_at < today_start
        )
        
        query = (
            update(User)
            .where(User.current_streak > 0)
            .where(User.id.not_in(subq))
            .values(current_streak=0)
        )
        
        result = await session.execute(query)
        count = result.rowcount
        
        if count > 0:
            await session.commit()
            logger.info("✅ Reset streak to 0 for %d users", count)
    
    return count


# ========== Новая задача: проверка дедлайнов ==========

@celery_app.task(name="tasks.check_upcoming_deadlines")
def check_upcoming_deadlines():
    """
    Cron-задача (запуск каждый час).
    Находит задачи с дедлайном через 2 часа (±10 минут) и отправляет уведомление.
    """
    try:
        result = asyncio.run(_check_upcoming_deadlines_async())
        return {"sent": result["sent"], "errors": result["errors"]}
    except Exception as exc:
        logger.error("Celery task check_upcoming_deadlines failed: %s", exc)
        raise


async def _check_upcoming_deadlines_async() -> dict:
    """Асинхронно проверяет дедлайны и отправляет уведомления."""
    
    now_utc = datetime.now(timezone.utc)
    
    # Интервал: от now+1h50m до now+2h10m (защита от смещения cron)
    start_window = now_utc + timedelta(hours=1, minutes=50)
    end_window = now_utc + timedelta(hours=2, minutes=10)
    
    sent_count = 0
    error_count = 0
    
    async with async_session_factory() as session:
        query = select(Task).where(
            Task.status == "active",
            Task.due_date.is_not(None),
            Task.due_date >= start_window,
            Task.due_date <= end_window,
        ).options(selectinload(Task.owner))
        
        result = await session.execute(query)
        tasks = result.scalars().all()
        
        for task in tasks:
            try:
                await send_task_deadline_reminder(task)
                sent_count += 1
                logger.info(f"📧 Уведомление о дедлайне: task={task.id}, user={task.owner_id}")
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Ошибка уведомления task={task.id}: {e}")
    
    return {"sent": sent_count, "errors": error_count}

@celery_app.task(name="tasks.reset_daily_limits")
def reset_daily_limits():
    """
    Синхронная версия без asyncio. Обнуляет daily_xp и daily_gold для всех пользователей.
    """
    from sqlalchemy import create_engine, text
    from app.core.config import settings

    # Берём синхронный URL (заменяем +asyncpg на +psycopg2)
    sync_url = settings.DATABASE_URL.replace("+asyncpg", "").replace(
        "postgresql+psycopg2", "postgresql"
    )
    engine = create_engine(sync_url)
    try:
        with engine.connect() as conn:
            result = conn.execute(text("UPDATE users SET daily_xp = 0, daily_gold = 0"))
            conn.commit()
            rowcount = result.rowcount
            logger.info(f"Reset daily limits: updated {rowcount} users")
            return {"status": "ok", "updated": rowcount}
    except Exception as e:
        logger.error(f"Reset daily limits failed: {e}")
        raise

async def _reset_daily_limits_async():
    async with async_session_factory() as session:
        # Обнуляем значения для всех пользователей
        await session.execute(
            update(User).values(
                daily_xp=0,
                daily_gold=0
            )
        )
        await session.commit()
        logger.info("✅ Дневные лимиты сброшены для всех пользователей")