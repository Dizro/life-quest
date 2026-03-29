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

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.task import Task
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
