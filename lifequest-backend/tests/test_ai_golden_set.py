"""
SCRUM-213: Регрессионное тестирование AI Effort Score.

Golden Set v1.0 — 50 эталонных задач от QA-инженера Эллины.

Режимы:
  - Обычный прогон (pytest):  мокирует LiteLLM → проверяет парсинг и валидацию
  - Live прогон (pytest -m live_ai):  реальный вызов YandexGPT → проверяет точность
"""
import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Optional

from app.schemas.ai import FALLBACK_EFFORT_SCORE, ComplexityLevel
from app.services.ai_service import get_effort_score, _parse_ai_json


# ─── Golden Set ──────────────────────────────────────────────────────────────
GOLDEN_SET = [
    # ID,  description,                                          expected, tolerance
    ("GS-001", "Купить продукты по списку (молоко, хлеб, яйца)", 2, 0),
    ("GS-002", "Вынести мусор", 1, 0),
    ("GS-003", "Записаться на прием к врачу через Госуслуги", 3, 1),
    ("GS-004", "Приготовить ужин на 2 персоны (паста с соусом)", 4, 1),
    ("GS-005", "Прогулка с собакой 30 минут", 2, 0),
    ("GS-006", "Уборка в одной комнате (пылесос и влажная уборка)", 5, 1),
    ("GS-007", "Оплата коммунальных платежей в приложении", 2, 0),
    ("GS-008", "Полив всех комнатных растений (15 горшков)", 3, 1),
    ("GS-009", "Смена постельного белья", 2, 0),
    ("GS-010", "Глажка 5 рубашек", 4, 1),
    ("GS-011", "Исправить опечатку в README.md", 1, 0),
    ("GS-012", "Провести Code Review небольшого PR (до 50 строк)", 5, 1),
    ("GS-013", "Создать новую ветку и настроить пустой проект React", 8, 2),
    ("GS-014", "Написать unit-тесты для функции валидации email (5 кейсов)", 6, 1),
    ("GS-015", "Исправить баг с отображением даты в Safari", 10, 2),
    ("GS-016", "Подготовить презентацию проекта на 5 слайдов", 12, 2),
    ("GS-017", "Провести созвон по планированию спринта (1 час)", 7, 1),
    ("GS-018", "Настроить Alias в .zshrc для базовых команд", 3, 0),
    ("GS-019", "Оптимизировать запрос к БД для поиска по индексам", 13, 3),
    ("GS-020", "Добавить иконку в футер сайта", 2, 0),
    ("GS-021", "Проектирование архитектуры микросервиса оплаты", 20, 2),
    ("GS-022", "Полный рефакторинг модуля авторизации на OAuth2/OIDC", 18, 3),
    ("GS-023", "Переезд с Jenkins на GitLab CI для всего проекта", 20, 2),
    ("GS-024", "Исследование и внедрение кеширования Redis для API", 15, 3),
    ("GS-025", "Подготовка годового финансового отчета департамента", 20, 0),
    ("GS-026", "Спланировать переезд офиса на 50 человек", 19, 2),
    ("GS-027", "Разработка мобильного приложения с нуля (MVP)", 20, 0),
    ("GS-028", "Настройка кластера Kubernetes в облаке", 17, 3),
    ("GS-029", "Проведение аудита безопасности системы", 18, 2),
    ("GS-030", "Интеграция с внешней CRM по протоколу SOAP", 16, 3),
    ("GS-031", "Посмотреть вебинар по новым фишкам Python 3.12", 5, 1),
    ("GS-032", "Прочитать 3 главы книги по архитектуре ПО", 8, 2),
    ("GS-033", "Пройти тест на знание SQL", 6, 1),
    ("GS-034", "Выучить 20 новых английских слов", 4, 1),
    ("GS-035", "Написать статью в блог компании про опыт с ИИ", 12, 2),
    ("GS-036", "Сделать утреннюю зарядку 15 минут", 3, 0),
    ("GS-037", "Решить 3 задачи на LeetCode (уровень Medium)", 10, 2),
    ("GS-038", "Посетить митап по DevOps", 7, 1),
    ("GS-039", "Начать изучать новый язык программирования (Go)", 12, 3),
    ("GS-040", "Разобрать старые закладки в браузере", 5, 2),
    ("GS-041", "Сходить в магазин", 2, 0),
    ("GS-042", "Построить космический корабль во дворе", 20, 0),
    ("GS-043", "...", 1, 0),
    ("GS-044", "Поморгать глазами", 1, 0),
    ("GS-045", "Изучить теорию струн с нуля", 20, 0),
    ("GS-046", "Исправить 500 ошибок линтера вручную", 15, 0),
    ("GS-047", "Позвонить в техподдержку провайдера", 4, 0),
    ("GS-048", "Организовать день рождения на 20 человек", 14, 0),
    ("GS-049", "Выпить стакан воды", 1, 0),
    ("GS-050", "Найти жизнь на Марсе", 20, 0),
]


def _make_ai_response(score: int, level: str = None) -> MagicMock:
    """Создаёт мок-ответ LiteLLM."""
    if level is None:
        if score <= 4:
            level = "Low"
        elif score <= 9:
            level = "Medium"
        elif score <= 14:
            level = "High"
        else:
            level = "Epic"

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "value": score,
        "confidence": 0.85,
        "reasoning": f"Оценка: {score}/20",
        "complexity_level": level,
        "detected_language": "ru",
    })
    mock_response.usage = MagicMock()
    mock_response.usage.total_tokens = 150
    return mock_response


# ─── Тесты парсера ───────────────────────────────────────────────────────────

class TestAIParser:
    """Юнит-тесты для парсинга JSON-ответов от ИИ."""

    def test_parse_valid_json(self):
        raw = '{"value": 8, "confidence": 0.9, "reasoning": "Средняя задача", "complexity_level": "Medium"}'
        result = _parse_ai_json(raw, "test task")
        assert result.value == 8
        assert result.confidence == 0.9
        assert result.complexity_level == ComplexityLevel.MEDIUM

    def test_parse_with_markdown_fence(self):
        raw = '```json\n{"value": 15, "confidence": 0.7, "reasoning": "Сложно", "complexity_level": "High"}\n```'
        result = _parse_ai_json(raw, "test task")
        assert result.value == 15

    def test_parse_with_preamble(self):
        raw = 'Конечно, вот оценка: {"value": 3, "confidence": 0.8, "reasoning": "Просто", "complexity_level": "Low"}'
        result = _parse_ai_json(raw, "test task")
        assert result.value == 3

    def test_value_clamped_above_20(self):
        raw = '{"value": 99, "confidence": 0.9, "reasoning": "test", "complexity_level": "Epic"}'
        result = _parse_ai_json(raw, "test task")
        assert result.value == 20

    def test_value_clamped_below_1(self):
        raw = '{"value": -5, "confidence": 0.9, "reasoning": "test", "complexity_level": "Low"}'
        result = _parse_ai_json(raw, "test task")
        assert result.value == 1

    def test_reasoning_truncated(self):
        long_reasoning = "А" * 300
        raw = json.dumps({
            "value": 5,
            "confidence": 0.8,
            "reasoning": long_reasoning,
            "complexity_level": "Medium",
        })
        result = _parse_ai_json(raw, "test task")
        assert len(result.reasoning) <= 255

    def test_invalid_complexity_level_uses_fallback(self):
        raw = '{"value": 5, "confidence": 0.8, "reasoning": "test", "complexity_level": "INVALID"}'
        with pytest.raises(Exception):
            _parse_ai_json(raw, "test task")


# ─── Mock тесты Golden Set ────────────────────────────────────────────────────

@pytest.mark.parametrize("task_id,description,expected_score,tolerance", GOLDEN_SET)
@pytest.mark.asyncio
async def test_golden_set_mock(task_id: str, description: str, expected_score: int, tolerance: int):
    """
    SCRUM-213: Мок-тесты Golden Set.
    Проверяют что парсер, валидация и fallback работают корректно.
    ИИ не вызывается — используется MagicMock.
    """
    mock_response = _make_ai_response(expected_score)

    with patch("app.services.ai_service.litellm.acompletion", new_callable=AsyncMock) as mock_completion:
        mock_completion.return_value = mock_response
        result = await get_effort_score(description)

    # Схема ответа соответствует контракту
    assert result.request_id is not None
    assert result.task_info.original_text == description
    assert result.effort_score is not None
    assert result.metadata is not None

    score = result.effort_score.value
    assert 1 <= score <= 20, f"[{task_id}] Score {score} выходит за диапазон 1-20"

    # Confidence и complexity_level в норме
    assert 0.0 <= result.effort_score.confidence <= 1.0
    assert result.effort_score.complexity_level in list(ComplexityLevel)
    assert len(result.effort_score.reasoning) <= 255


@pytest.mark.asyncio
async def test_fallback_on_timeout():
    """SCRUM-212: При таймауте возвращается безопасный fallback."""
    from litellm.exceptions import Timeout

    with patch("app.services.ai_service.litellm.acompletion", new_callable=AsyncMock) as mock_completion:
        mock_completion.side_effect = Timeout(message="timeout", model="test", llm_provider="yandex")
        result = await get_effort_score("Написать код")

    assert result.effort_score.value == 5
    assert result.effort_score.confidence == 0.0
    assert "таймаут" in result.effort_score.reasoning.lower() or "умолчанию" in result.effort_score.reasoning.lower()


@pytest.mark.asyncio
async def test_fallback_on_invalid_json():
    """SCRUM-212: При невалидном JSON от ИИ — fallback, не падение."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Извините, я не могу оценить эту задачу."
    mock_response.usage = MagicMock()
    mock_response.usage.total_tokens = 20

    with patch("app.services.ai_service.litellm.acompletion", new_callable=AsyncMock) as mock_completion:
        mock_completion.return_value = mock_response
        result = await get_effort_score("Задача с галлюцинацией ИИ")

    assert result.effort_score.value == 5
    assert result.effort_score.confidence == 0.0


@pytest.mark.asyncio
async def test_fallback_on_quota_exceeded():
    """SCRUM-212: При превышении квоты — fallback без исключения."""
    from litellm.exceptions import RateLimitError

    with patch("app.services.ai_service.litellm.acompletion", new_callable=AsyncMock) as mock_completion:
        mock_completion.side_effect = RateLimitError(
            message="quota exceeded", model="test", llm_provider="yandex"
        )
        result = await get_effort_score("Задача при квоте")

    assert result.effort_score.value == 5


@pytest.mark.asyncio
async def test_ai_response_full_contract():
    """Полная проверка JSON-контракта согласно схеме Эллины."""
    mock_response = _make_ai_response(13, "High")

    with patch("app.services.ai_service.litellm.acompletion", new_callable=AsyncMock) as mock_completion:
        mock_completion.return_value = mock_response
        result = await get_effort_score("Рефакторинг модуля авторизации с JWT на OAuth2")

    # Полный контракт
    assert result.request_id  # UUID
    assert result.task_info.original_text
    assert result.task_info.detected_language in ("ru", "en")

    es = result.effort_score
    assert 1 <= es.value <= 20
    assert 0.0 <= es.confidence <= 1.0
    assert es.complexity_level in list(ComplexityLevel)
    assert 1 <= len(es.reasoning) <= 255

    meta = result.metadata
    assert meta.model_version == "yandexgpt-5-lite"
    assert meta.tokens_used >= 0
    assert meta.latency_ms >= 0


# ─── Live тесты (реальный вызов YandexGPT) ───────────────────────────────────
# Запуск: pytest tests/test_ai_golden_set.py -m live_ai -v

LIVE_GOLDEN_SUBSET = [
    ("GS-002", "Вынести мусор", 1, 0),
    ("GS-011", "Исправить опечатку в README.md", 1, 0),
    ("GS-012", "Провести Code Review небольшого PR (до 50 строк)", 5, 1),
    ("GS-015", "Исправить баг с отображением даты в Safari", 10, 2),
    ("GS-021", "Проектирование архитектуры микросервиса оплаты", 20, 2),
    ("GS-025", "Подготовка годового финансового отчета департамента", 20, 0),
    ("GS-044", "Поморгать глазами", 1, 0),
    ("GS-049", "Выпить стакан воды", 1, 0),
]


@pytest.mark.live_ai
@pytest.mark.parametrize("task_id,description,expected_score,tolerance", LIVE_GOLDEN_SUBSET)
@pytest.mark.asyncio
async def test_golden_set_live(task_id: str, description: str, expected_score: int, tolerance: int):
    """
    SCRUM-213: Живые тесты Golden Set против реального YandexGPT.
    Запуск только с флагом -m live_ai для избежания трат токенов в CI.
    """
    result = await get_effort_score(description)
    actual_score = result.effort_score.value

    assert 1 <= actual_score <= 20, f"[{task_id}] Score {actual_score} выходит за диапазон"

    assert abs(actual_score - expected_score) <= tolerance, (
        f"[{task_id}] '{description[:40]}...'\n"
        f"  Ожидалось: {expected_score} ± {tolerance}\n"
        f"  Получено:  {actual_score}\n"
        f"  Обоснование: {result.effort_score.reasoning}"
    )