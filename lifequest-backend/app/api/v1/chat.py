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
    Передаём максимум информации, чтобы Фаррикс знал всё о герое.
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

    # Активные задачи (текущие квесты)
    active_tasks_result = await db.execute(
        select(Task.title, Task.task_type, Task.complexity_level)
        .where(Task.user_id == user.id, Task.status == "active")
        .order_by(Task.created_at.desc())
        .limit(10)
    )
    active_tasks = [f"{row[0]} ({row[1]}, {row[2] or '?'})" for row in active_tasks_result.fetchall()]

    # Количество активных испытаний (просроченные)
    trials_result = await db.execute(
        select(sql_func.count(Task.id))
        .where(Task.user_id == user.id, Task.status == "trial")
    )
    active_trials_count = trials_result.scalar() or 0

    # Общее кол-во выполненных задач
    total_completed_result = await db.execute(
        select(sql_func.count(Task.id))
        .where(Task.user_id == user.id, Task.status == "completed")
    )
    total_completed = total_completed_result.scalar() or 0

    # Экипировка
    equipment = []
    if user.equipped_hat:
        equipment.append(f"Шлем: {user.equipped_hat}")
    if user.equipped_armor:
        equipment.append(f"Броня: {user.equipped_armor}")
    if user.equipped_weapon:
        equipment.append(f"Оружие: {user.equipped_weapon}")
    if user.equipped_pet:
        equipment.append(f"Питомец: {user.equipped_pet}")
    if user.equipped_background:
        equipment.append(f"Фон: {user.equipped_background}")
    equipment_str = ", ".join(equipment) if equipment else "ничего не надето"

    # XP-множитель
    xp_buff = ""
    if user.xp_multiplier and user.xp_multiplier > 1.0:
        xp_buff = f"×{user.xp_multiplier} XP (активен бафф)"
    else:
        xp_buff = "нет"

    daily_xp_limit = 200 + user.level * 20
    xp_progress = f"{user.xp}/{user.xp_to_next_level}"

    # Возраст аккаунта
    account_days = (datetime.now(timezone.utc) - user.created_at).days if user.created_at else 0

    name = user.display_name or user.username

    system_prompt = f"""Ты — Фаррикс, ИИ-наставник в RPG-приложении LifeQuest. 
Твоя задача: поддерживать и вдохновлять пользователя (героя) в его повседневных делах, используя лёгкую игровую стилистику.

Правила:
- Длина ответа — 1–3 коротких предложения. Можно больше, если пользователь задаёт сложный вопрос.
- Обращайся к пользователю по имени: {name}.
- Используй игровую терминологию: квест, подвиг, дракон, опыт, уровень.
- Тон: поддержка, похвала, лёгкий юмор, воодушевление. Без сарказма и критики.
- Если пользователь спрашивает о своих характеристиках — отвечай точными данными из контекста ниже.
- Можешь давать советы по продуктивности и тайм-менеджменту в игровом стиле.
- Запрещены: политика, религия, оскорбления, советы по здоровью, финансы, интим, насилие, наркотики, реклама.

═══ Полный профиль героя ═══
- Имя: {name}
- Класс: {user.character_class}
- Звание: {user.rank_title}
- Уровень: {user.level}
- XP: {xp_progress} до следующего уровня
- Золото: {user.gold} 💰
- Кристаллы: {user.crystals} 💎
- Стрик (текущий): {user.streak_days} дней
- Макс. стрик: {user.max_streak} дней
- XP за сегодня: {user.daily_xp_earned} / {daily_xp_limit}
- XP бафф: {xp_buff}
- Дней в игре: {account_days}
- Всего квестов выполнено: {total_completed}

═══ Экипировка ═══
{equipment_str}

═══ Активные квесты (до 10) ═══
{chr(10).join(f'• {t}' for t in active_tasks) if active_tasks else 'Нет активных квестов'}

═══ Испытания (просрочено) ═══
Количество: {active_trials_count}

═══ Последние выполненные квесты ═══
{chr(10).join(f'✓ {t}' for t in last_tasks) if last_tasks else 'Пока нет выполненных квестов'}"""

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