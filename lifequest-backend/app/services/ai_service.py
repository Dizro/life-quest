"""
app/services/ai_service.py

Сервис оценки Effort Score через YandexGPT 5 Lite.

Промпт строго по ТЗ §7.1.
Таймаут 3 сек → fallback ES=5 (по ТЗ UC-14, п.43).

Используется нативный REST API YandexGPT:
  POST https://llm.api.cloud.yandex.net/foundationModels/v1/completion

Ключевые правила:
  - ES фиксируется ОДИН РАЗ при создании (§6.11, Слой 1)
  - При статусе «Испытание» ES НЕ пересчитывается (FR-3.4)
  - Кэш: если текст изменён ≤20% символов → новый запрос не нужен (§7.3)
  - ES=0 → бессмыслица/спам. Задача сохраняется, награда=0 (FR-3.3)
"""

from __future__ import annotations

import logging
import re

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── системный промпт для оценки ES (ТЗ §7.1) ────────────────────────────────

SYSTEM_PROMPT = """Ты — объективный оценщик сложности задач для продуктивного приложения.
Оценивай ТОЛЬКО по реальным временным и когнитивным затратам.
Не учитывай длину текста — короткое название может описывать сложное дело.

ШКАЛА:
  0   = бессмыслица, спам, одно слово без контекста, набор символов
  1-2 = микродействие до 5 мин (выпить воду, принять таблетку)
  3-4 = простая задача 15–30 мин (ответить на письмо, прогулка)
  5-6 = средняя задача 1–2 часа (прочитать главу, краткий отчёт)
  7-8 = сложная задача 3–8 часов (написать реферат, сдать лабораторную)
  9-10= масштабный проект дни/недели (глава диплома, большой проект)

Ответь строго в 2 строки без лишних символов и скобок:
SCORE: число от 0 до 10
REASON: одно предложение на русском"""

DEFAULT_ES = 5
AI_TIMEOUT_SECONDS = 3.0
YANDEX_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


# ── парсинг ответа ────────────────────────────────────────────────────────────

def _parse_score(text: str) -> int:
    """
    Извлекает число после 'SCORE:'.
    При ошибке парсинга → DEFAULT_ES (по ТЗ §7.1).
    """
    match = re.search(r"SCORE:\s*\[?(\d{1,2})\]?", text, re.IGNORECASE)
    if match:
        score = int(match.group(1))
        return max(0, min(10, score))
    return DEFAULT_ES


def _parse_reason(text: str) -> str:
    """Извлекает обоснование после 'REASON:'."""
    match = re.search(r"REASON:\s*\[?([^\]]+)\]?", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


# ── кэш-проверка: изменено ≤20% символов → не запрашивать (§7.3) ─────────────

def should_reevaluate(old_title: str, new_title: str) -> bool:
    """
    Возвращает True, если текст изменён более чем на 20% символов.
    По §7.3 — если ≤20% → кэшированный ES остаётся.
    """
    if not old_title or not new_title:
        return True
    max_len = max(len(old_title), len(new_title))
    if max_len == 0:
        return False
    # простая метрика: количество различающихся символов
    diff_chars = sum(1 for a, b in zip(old_title, new_title) if a != b)
    diff_chars += abs(len(old_title) - len(new_title))
    change_ratio = diff_chars / max_len
    return change_ratio > 0.20


# ── основной вызов к YandexGPT (нативный REST API) ───────────────────────────

async def evaluate_effort_score(task_title: str) -> tuple[int, str]:
    """
    Отправляет текст задачи в YandexGPT 5 Lite и возвращает (ES, reason).

    Используется нативный REST API:
      POST https://llm.api.cloud.yandex.net/foundationModels/v1/completion

    Таймаут 3 сек:
      - при превышении → ES=5 по умолчанию (UC-14, п.43)
      - при любой ошибке ИИ → ES=5 по умолчанию

    Returns:
        tuple[int, str]: (effort_score 0-10, краткое обоснование)
    """
    if not settings.YANDEX_API_KEY or not settings.YANDEX_FOLDER_ID:
        logger.warning(
            "YANDEX_API_KEY / YANDEX_FOLDER_ID не заданы — используем ES=%d по умолчанию",
            DEFAULT_ES,
        )
        return DEFAULT_ES, "ИИ-оценка недоступна: ключи не настроены"

    try:
        async with httpx.AsyncClient(timeout=AI_TIMEOUT_SECONDS) as client:
            response = await client.post(
                YANDEX_API_URL,
                headers={
                    "Authorization": f"Api-Key {settings.YANDEX_API_KEY}",
                    "x-folder-id": settings.YANDEX_FOLDER_ID,
                    "Content-Type": "application/json",
                },
                json={
                    "modelUri": f"gpt://{settings.YANDEX_FOLDER_ID}/yandexgpt-5-lite/latest",
                    "completionOptions": {
                        "stream": False,
                        "temperature": 0.3,
                        "maxTokens": "100",
                    },
                    "messages": [
                        {"role": "system", "text": SYSTEM_PROMPT},
                        {"role": "user", "text": f"Задача: {task_title}"},
                    ],
                },
            )

        if response.status_code != 200:
            logger.error(
                "YandexGPT HTTP %d: %s → ES=%d",
                response.status_code, response.text[:200], DEFAULT_ES,
            )
            return DEFAULT_ES, "Ошибка ИИ — назначена оценка по умолчанию"

        data = response.json()
        text = data["result"]["alternatives"][0]["message"]["text"]

        score = _parse_score(text)
        reason = _parse_reason(text)

        logger.info("ES оценка: task=%r → SCORE=%d, REASON=%s", task_title, score, reason)
        return score, reason

    except httpx.TimeoutException:
        logger.warning("YandexGPT таймаут (>%.1f сек) для задачи %r → ES=%d", AI_TIMEOUT_SECONDS, task_title, DEFAULT_ES)
        return DEFAULT_ES, "Таймаут ИИ — назначена оценка по умолчанию"

    except Exception as exc:
        logger.error("Ошибка YandexGPT для задачи %r: %s → ES=%d", task_title, exc, DEFAULT_ES)
        return DEFAULT_ES, "Ошибка ИИ — назначена оценка по умолчанию"

