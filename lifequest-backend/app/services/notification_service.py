"""
Сервис отправки push-уведомлений через FCM и WebPush.
В случае отсутствия конфигурации – логирует и возвращает False.
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.device_token import DeviceToken
from app.models.task import Task
from app.models.user import User

logger = logging.getLogger(__name__)

# Попытка импорта FCM и WebPush (с подавлением ошибок, если не установлены)
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FCM_AVAILABLE = True
except ImportError:
    FCM_AVAILABLE = False
    logger.warning("Firebase Admin SDK не установлен. FCM уведомления недоступны.")

try:
    from pywebpush import webpush, WebPushException
    WEBPUSH_AVAILABLE = True
except ImportError:
    WEBPUSH_AVAILABLE = False
    logger.warning("pywebpush не установлен. WebPush уведомления недоступны.")


# Инициализация Firebase (если есть credentials)
_firebase_app = None
if FCM_AVAILABLE and settings.FIREBASE_CREDENTIALS_PATH:
    try:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase инициализирован")
    except Exception as e:
        logger.error(f"Ошибка инициализации Firebase: {e}")


async def send_notification(
    user_id: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> bool:
    """
    Отправляет push-уведомление пользователю на все его зарегистрированные устройства.
    Возвращает True, если хотя бы одно уведомление отправлено успешно.
    """
    async with async_session_factory() as session:
        result = await session.execute(
            select(DeviceToken).where(DeviceToken.user_id == user_id)
        )
        tokens = result.scalars().all()

    if not tokens:
        logger.info(f"Нет зарегистрированных устройств для user_id={user_id}")
        return False

    success = False
    for device in tokens:
        if device.platform in ("ios", "android"):
            if FCM_AVAILABLE and _firebase_app:
                try:
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=title,
                            body=body,
                        ),
                        data=data or {},
                        token=device.token,
                    )
                    response = messaging.send(message)
                    logger.info(f"FCM уведомление отправлено: {response}")
                    success = True
                except Exception as e:
                    logger.error(f"Ошибка отправки FCM: {e}")
            else:
                logger.debug(f"FCM не доступен, пропускаем токен {device.token}")
        elif device.platform == "web":
            if WEBPUSH_AVAILABLE and settings.VAPID_PRIVATE_KEY and settings.VAPID_PUBLIC_KEY:
                try:
                    webpush(
                        subscription_info=device.token,  # ожидается dict или строка JSON
                        data=body,
                        vapid_private_key=settings.VAPID_PRIVATE_KEY,
                        vapid_claims={
                            "sub": f"mailto:{settings.VAPID_EMAIL}"
                        },
                    )
                    logger.info(f"WebPush уведомление отправлено на {device.token}")
                    success = True
                except WebPushException as e:
                    logger.error(f"Ошибка WebPush: {e}")
            else:
                logger.debug("WebPush не доступен, пропускаем")
        else:
            logger.warning(f"Неизвестная платформа: {device.platform}")

    return success


# --- Удобные обёртки для конкретных сценариев ---

async def send_task_deadline_reminder(task: Task) -> bool:
    """Отправляет напоминание о приближающемся дедлайне."""
    user = task.owner
    title = "Дедлайн приближается!"
    body = f"До выполнения квеста '{task.title}' осталось 2 часа"
    data = {"task_id": str(task.id), "type": "deadline"}
    return await send_notification(str(user.id), title, body, data)


async def send_evening_reminder(user: User, streak: int) -> bool:
    """Отправляет вечернее напоминание."""
    title = "Не теряй свой стрик!"
    body = f"{user.display_name or user.username}, твой стрик уже {streak} дней. Зайди и выполни задачу!"
    return await send_notification(str(user.id), title, body, None)


async def send_trial_reminder(user: User, trials_count: int) -> bool:
    """Отправляет напоминание о накопившихся испытаниях."""
    title = "Испытания ждут!"
    body = f"У тебя {trials_count} испытаний. Разберись с ними, пока не стало поздно!"
    return await send_notification(str(user.id), title, body, None)


async def send_achievement_notification(user: User, achievement_title: str, xp_bonus: int) -> bool:
    """Отправляет уведомление о получении достижения."""
    title = "Новое достижение!"
    body = f"Ты получил достижение '{achievement_title}' и бонус +{xp_bonus} XP!"
    data = {"type": "achievement"}
    return await send_notification(str(user.id), title, body, data)