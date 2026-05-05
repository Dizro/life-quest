"""
Чат с Фарриксом (FR-4.2, UC-16).

Лимит: 5 запросов в сутки для бесплатного уровня.
Лимит хранится в Redis через INCR + TTL до конца UTC-дня (атомарно — нет гонок).
Контекст передаётся согласно разделу 7.2 ТЗ.
"""

import json
import logging
from datetime import datetime, timezone
from typing import List, Optional

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.api.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

FREE_DAILY_LIMIT = 5  # FR-4.2


class ChatMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []   # Последние 10 сообщений от клиента


class ChatResponse(BaseModel):
    reply: str
    requests_used: int
    requests_limit: int
    requests_remaining: int


async def _get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


def _seconds_until_utc_midnight() -> int:
    """Секунд до 00:00 UTC — TTL для счётчика суточного лимита."""
    now = datetime.now(timezone.utc)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    from datetime import timedelta
    next_midnight = midnight + timedelta(days=1)
    return int((next_midnight - now).total_seconds())


async def _check_and_increment_limit(user_id: int, redis: aioredis.Redis) -> int:
    """
    Атомарно инкрементирует счётчик запросов пользователя за сутки.
    Возвращает текущее значение счётчика после инкремента.
    Использует INCR + EXPIREAT для атомарности (нет гонок при конкурентных запросах).
    """
    key = f"chat_limit:{user_id}:{datetime.now(timezone.utc).date().isoformat()}"
    count = await redis.incr(key)
    if count == 1:
        # Первый запрос за сутки — выставляем TTL до конца дня
        await redis.expire(key, _seconds_until_utc_midnight())
    return count


async def _build_farrix_prompt(user: User, db: AsyncSession, user_message: str, history: List[ChatMessage]) -> str:
    """
    Формирует системный промпт с контекстом пользователя (раздел 7.2 ТЗ).
    НЕ передаётся: полная история задач, архив, данные других пользователей.
    """
    # Последние 5 завершённых задач
    last_tasks_result = await db.execute(
        select(Task.title)
        .where(Task.user_id == user.id, Task.status == "completed")
        .order_by(Task.completed_at.desc())
        .limit(5)
    )
    last_tasks = [row[0] for row in last_tasks_result.fetchall()]

    # Количество активных испытаний
    trials_result = await db.execute(
        select(sql_func.count(Task.id))
        .where(Task.user_id == user.id, Task.status == "trial")
    )
    active_trials_count = trials_result.scalar() or 0

    context = {
        "user_level": user.level,
        "current_streak": user.streak_days,
        "active_trials_count": active_trials_count,
        "last_5_completed_tasks": last_tasks,
        "current_daily_xp": user.daily_xp_earned,
        "daily_xp_limit": 200 + user.level * 20,
    }

    system_prompt = f"""Ты — Фаррикс, ИИ-наставник в RPG-приложении LifeQuest. 
Твоя задача: поддерживать и вдохновлять пользователя (героя) в его повседневных делах, используя лёгкую игровую стилистику.

Правила:
- Длина ответа — 1–2 коротких предложения.
- Обращайся к пользователю по имени: {user.display_name or user.username}.
- Используй игровую терминологию: квест, подвиг, дракон, опыт, уровень.
- Тон: поддержка, похвала, лёгкий юмор, воодушевление. Без сарказма и критики.
- Запрещены: политика, религия, оскорбления, советы по здоровью, финансы, интим, насилие, наркотики, реклама.

Контекст пользователя:
- Уровень: {context['user_level']}
- Текущий стрик: {context['current_streak']}
- Активных испытаний: {context['active_trials_count']}
- Последние выполненные задачи: {', '.join(context['last_5_completed_tasks']) or 'нет'}
- XP за сегодня: {context['current_daily_xp']} / {context['daily_xp_limit']}"""

    return system_prompt


@router.post("/", response_model=ChatResponse)
async def chat_with_farrix(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Диалог с Фарриксом.
    Бесплатный уровень: 5 запросов/сутки.
    Лимит хранится в Redis атомарно (INCR).
    """
    redis = await _get_redis()
    try:
        count = await _check_and_increment_limit(current_user.id, redis)
    except Exception as e:
        logger.error("Redis error in chat limit check: %s", e)
        count = 1  # При ошибке Redis — не блокируем пользователя
    finally:
        await redis.aclose()

    if count > FREE_DAILY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Достигнут дневной лимит диалогов с Фарриксом ({FREE_DAILY_LIMIT}/день). Обнови подписку до Pro.",
        )

    system_prompt = await _build_farrix_prompt(current_user, db, request.message, request.history)

    # Формируем историю сообщений (берём последние 10, раздел 7.2)
    messages = [{"role": "system", "text": system_prompt}]
    for msg in request.history[-10:]:
        messages.append({"role": msg.role, "text": msg.content})
    messages.append({"role": "user", "text": request.message})

    reply = await _call_yandex_gpt(messages)

    return ChatResponse(
        reply=reply,
        requests_used=count,
        requests_limit=FREE_DAILY_LIMIT,
        requests_remaining=max(0, FREE_DAILY_LIMIT - count),
    )


async def _call_yandex_gpt(messages: list) -> str:
    """Прямой вызов YandexGPT с fallback."""
    if not settings.YANDEX_API_KEY or not settings.YANDEX_FOLDER_ID:
        return _farrix_fallback()

    model_uri = f"gpt://{settings.YANDEX_FOLDER_ID}/yandexgpt-5-lite/latest"

    try:
        async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
            res = await client.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                headers={
                    "Authorization": f"Api-Key {settings.YANDEX_API_KEY}",
                    "x-data-logging-enabled": "false",
                },
                json={
                    "modelUri": model_uri,
                    "completionOptions": {
                        "temperature": 0.7,
                        "maxTokens": 400,
                    },
                    "messages": messages,
                },
            )
            res.raise_for_status()
            data = res.json()
            return data["result"]["alternatives"][0]["message"]["text"]
    except Exception as e:
        logger.warning("Farrix chat API error: %s", e)
        return _farrix_fallback()


def _farrix_fallback() -> str:
    import random
    phrases = [
        "Твоя сила в последовательности. Каждый день — маленькая победа.",
        "Герои не рождаются — они куются в ежедневных делах.",
        "Расскажи мне подробнее о своей задаче, и я помогу её разбить на шаги.",
        "Сегодняшние трудности — завтрашние навыки. Продолжай!",
        "Выполни хотя бы одно дело сегодня — и стрик останется жить.",
    ]
    return random.choice(phrases)