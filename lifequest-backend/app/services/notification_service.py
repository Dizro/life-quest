"""
app/services/notification_service.py

Сервис для отправки push-уведомлений пользователям.
В MVP версии — заглушка (логирование), в продакшене — интеграция с FCM/APNS/WebPush.
"""

import logging
from typing import Optional

from app.models.task import Task
from app.models.user import User

logger = logging.getLogger(__name__)


async def send_task_deadline_reminder(task: Task) -> bool:
    """
    Отправляет уведомление пользователю о том, что до дедлайна задачи осталось 2 часа.
    
    Args:
        task: задача с приближающимся дедлайном
        
    Returns:
        True если уведомление отправлено, иначе False
    """
    user = task.owner
    if not user:
        logger.warning(f"Задача {task.id}: пользователь не найден")
        return False
    
    # TODO: В продакшене заменить на реальную отправку через FCM/APNS/WebPush
    # Сейчас только логируем (заглушка для MVP)
    
    logger.info(
        f"🔔 [Уведомление о дедлайне] Пользователь: {user.username}, "
        f"Задача: '{task.title}', Дедлайн: {task.due_date}"
    )
    
    # Здесь в будущем будет реальный вызов push-сервиса:
    # await push_service.send(
    #     user_id=user.id,
    #     title="Дедлайн приближается!",
    #     body=f"До выполнения квеста '{task.title}' осталось 2 часа",
    #     data={"task_id": str(task.id), "type": "deadline"}
    # )
    
    return True


async def send_evening_reminder(user: User, streak: int) -> bool:
    """Отправляет вечернее напоминание, если пользователь не был активен сегодня."""
    logger.info(
        f"🔔 [Вечернее напоминание] Пользователь: {user.username}, "
        f"Текущий стрик: {streak}"
    )
    return True


async def send_trial_reminder(user: User, trials_count: int) -> bool:
    """Отправляет напоминание о накопившихся испытаниях."""
    logger.info(
        f"🔔 [Напоминание об испытаниях] Пользователь: {user.username}, "
        f"Количество испытаний: {trials_count}"
    )
    return True


async def send_achievement_notification(user: User, achievement_title: str, reward: int) -> bool:
    """Отправляет уведомление о получении достижения."""
    logger.info(
        f"🔔 [Достижение] Пользователь: {user.username}, "
        f"Достижение: '{achievement_title}', Награда: +{reward} XP"
    )
    return True