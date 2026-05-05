import asyncio
import json
import time
import uuid
import logging
import httpx

import litellm
from litellm.exceptions import Timeout, RateLimitError, APIError

from app.core.config import settings
from app.schemas.ai import (
    AIResponse, EffortScoreData, TaskInfo, AIMetadata,
    ComplexityLevel, FALLBACK_EFFORT_SCORE
)

logger = logging.getLogger(__name__)
litellm.suppress_debug_info = True


def _build_effort_score_prompt(task_description: str) -> str:
    return f"""Ты — строгий ИИ-наставник системы LifeQuest. 
Оцени сложность задачи от 1 до 20 по следующим жестким правилам:

ШКАЛА ОЦЕНОК (СТРОГО СОБЛЮДАЙ):
1-3: Элементарные, минутные действия (исправить опечатку, выпить воды, поморгать).
4-7: Простые рутинные или бытовые задачи (уборка, мелкий багфикс, созвон).
8-12: Средние задачи, требующие пары часов и фокуса (написать тесты, решить баг в браузере).
13-17: Сложные задачи (оптимизация БД, аналитика, написание статьи).
18-20: Эпичные, масштабные проекты (проектирование архитектуры микросервисов, разработка с нуля, годовой отчет, колонизация Марса).

ВАЖНО: Не занижай оценки для масштабных проектов (смело ставь 19-20) и не завышай для минутных дел и опечаток (ставь 1-2). Твоя оценка должна быть максимально контрастной.

Задача: "{task_description}"

Ответь СТРОГО в формате JSON без дополнительного текста:
{{
  "value": <целое число 1-20>,
  "confidence": <число 0.0-1.0>,
  "reasoning": "<краткое обоснование почему выбрана именно эта оценка, до 200 символов>",
  "complexity_level": "<Low|Medium|High|Epic>",
  "detected_language": "<ru|en>"
}}"""


def _parse_ai_json(raw_text: str, task_description: str) -> EffortScoreData:
    text = raw_text.strip()
    if "```" in text:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]
    elif not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]

    data = json.loads(text)

    return EffortScoreData(
        value=data.get("value", 5),
        confidence=data.get("confidence", 0.5),
        reasoning=data.get("reasoning", "Оценка выполнена"),
        complexity_level=data.get("complexity_level", "Medium"),
    )


async def get_effort_score(task_description: str) -> AIResponse:
    request_id = str(uuid.uuid4())
    detected_language = "ru" if any(ord(c) > 127 for c in task_description) else "en"
    start_time = time.monotonic()

    model_uri = f"gpt://{settings.YANDEX_FOLDER_ID}/yandexgpt-5-lite/latest"
    prompt = _build_effort_score_prompt(task_description)

    effort_data: EffortScoreData = FALLBACK_EFFORT_SCORE
    tokens_used = 0
    raw_text = ""

    try:
        try:
            # 1. Попытка вызова через LiteLLM (маршрутизатор)
            response = await litellm.acompletion(
                model=f"yandex/{model_uri}",
                messages=[{"role": "user", "content": prompt}],
                api_key=settings.YANDEX_API_KEY,
                timeout=settings.AI_TIMEOUT_SECONDS,
                max_tokens=300,
                temperature=0.1,
            )
            raw_text = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0

        except Exception as llm_err:
            # 2. Непробиваемый Fallback: Если версия LiteLLM не понимает Yandex
            if "LLM Provider NOT provided" in str(llm_err) or "Unmapped" in str(llm_err):
                logger.info("LiteLLM fallback: Direct HTTPX request to Yandex Cloud.")
                async with httpx.AsyncClient() as client:
                    res = await client.post(
                        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                        headers={
                            "Authorization": f"Api-Key {settings.YANDEX_API_KEY}",
                            "x-data-logging-enabled": "false"
                        },
                        json={
                            "modelUri": model_uri,
                            "completionOptions": {"temperature": 0.1, "maxTokens": 300},
                            "messages": [{"role": "user", "text": prompt}]
                        },
                        timeout=settings.AI_TIMEOUT_SECONDS
                    )
                    res.raise_for_status()
                    data = res.json()
                    raw_text = data["result"]["alternatives"][0]["message"]["text"]
                    tokens_used = int(data["result"]["usage"]["totalTokens"])
            else:
                raise llm_err  # Пробрасываем другие ошибки (Timeout, RateLimit) дальше

        # Общий парсинг результата (что от LiteLLM, что от HTTPX)
        try:
            effort_data = _parse_ai_json(raw_text, task_description)
        except (json.JSONDecodeError, KeyError, ValueError) as parse_err:
            logger.warning("AI_INVALID_FORMAT: failed to parse AI response: %s", parse_err)
            effort_data = FALLBACK_EFFORT_SCORE

    except Timeout:
        logger.warning("AI_TIMEOUT: YandexGPT timeout")
        effort_data = FALLBACK_EFFORT_SCORE

    except RateLimitError:
        logger.error("AI_QUOTA_EXCEEDED: YandexGPT rate limit hit")
        effort_data = FALLBACK_EFFORT_SCORE

    except Exception as e:
        logger.error("AI_UNEXPECTED_ERROR: %s", str(e))
        effort_data = FALLBACK_EFFORT_SCORE

    latency_ms = int((time.monotonic() - start_time) * 1000)

    return AIResponse(
        request_id=request_id,
        task_info=TaskInfo(
            original_text=task_description,
            detected_language=detected_language,
        ),
        effort_score=effort_data,
        metadata=AIMetadata(
            model_version="yandexgpt-5-lite",
            tokens_used=tokens_used,
            latency_ms=latency_ms,
        ),
    )