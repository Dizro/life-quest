"""
app/tasks/celery_tasks.py

Celery-задача для асинхронной оценки Effort Score после создания задачи.

Поток по BPMN:
  Клиент создаёт задачу → API сохраняет со status=pending_es →
  → Celery-задача вызывает YandexGPT → обновляет effort_score в БД →
  → status=active (или active при ES=0 с нулевой наградой).

Правила:
  - ES фиксируется ОДИН РАЗ при создании (§6.11, Слой 1)
  - При таймауте >3 сек → ES=5 по умолчанию (UC-14)
  - ES=0 → бессмыслица, награда = 0, Фаррикс уведомляет (FR-3.3)
"""

from __future__ import annotations

import asyncio
import logging
import uuid

from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.task import Task
from app.models.user import User
from app.services.ai_service import evaluate_effort_score

logger = logging.getLogger(__name__)


@celery_app.task(
    name="tasks.evaluate_es",
    bind=True,
    max_retries=2,
    default_retry_delay=5,
    acks_late=True,
)
def evaluate_es_task(self, task_id: str, task_title: str) -> dict:
    """
    Запрашивает Effort Score у YandexGPT и сохраняет в БД.

    Args:
        task_id: UUID задачи (строка)
        task_title: текст задачи для оценки

    Returns:
        dict с результатом: {"task_id": ..., "effort_score": ..., "reason": ...}
    """
    try:
        result = asyncio.run(_evaluate_and_save(task_id, task_title))
        return result
    except Exception as exc:
        logger.error("Celery task evaluate_es failed for %s: %s", task_id, exc)
        # retry с экспоненциальным backoff
        raise self.retry(exc=exc)


async def _evaluate_and_save(task_id: str, task_title: str) -> dict:
    """Асинхронно оценивает ES и обновляет задачу в БД."""

    # 1. Получить ES от YandexGPT (таймаут 3 сек внутри)
    es, reason = await evaluate_effort_score(task_title)

    # 2. Обновить задачу в БД
    async with async_session_factory() as session:
        result = await session.execute(
            select(Task).where(Task.id == uuid.UUID(task_id))
        )
        task = result.scalar_one_or_none()

        if not task:
            logger.warning("Task %s not found in DB — skipping ES update", task_id)
            return {"task_id": task_id, "effort_score": None, "reason": "task not found"}

        task.effort_score = es
        # Переводим в active из pending_es (если был pending)
        if task.status.value == "pending_es":
            task.status = "active"

        session.add(task)
        await session.commit()

        logger.info(
            "✅ ES updated: task=%s, score=%d, reason=%s",
            task_id, es, reason,
        )

    return {"task_id": task_id, "effort_score": es, "reason": reason}

@celery_app.task(name="tasks.transition_overdue_tasks_to_trial")
def transition_overdue_tasks_to_trial():
    """
    Cron-задача (00:01 ежедневно).
    Переводит активные просроченные задачи (с due_date в прошлом) в статус 'trial'.
    (Только `task_type` IN ['regular', 'daily']).
    """
    try:
        count = asyncio.run(_transition_overdue_tasks_to_trial_async())
        return {"processed": count}
    except Exception as exc:
        logger.error("Celery task transition_overdue_tasks_to_trial failed: %s", exc)
        raise

async def _transition_overdue_tasks_to_trial_async() -> int:
    now_utc = datetime.now(timezone.utc)
    
    async with async_session_factory() as session:
        # Ищем задачи для перевода:
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
    """
    Cron-задача (00:05 ежедневно).
    Сбрасывает current_streak в 0 тем пользователям, которые вчера
    НЕ выполнили ни одной ежедневной задачи.
    """
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

