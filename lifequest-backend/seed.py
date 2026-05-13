"""
seed.py — наполнение базы стартовыми и тестовыми данными.

Запуск внутри Docker:
    docker-compose exec api python seed.py

Идемпотентен: повторный запуск не создаёт дубли.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import get_password_hash
from app.models.achievement import Achievement
from app.models.task import Task
from app.models.user import User

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s [%(name)s] %(message)s",
)
logger = logging.getLogger("seed")


# ── каталог достижений ────────────────────────────────────────────────────────

INITIAL_ACHIEVEMENTS = [
    # Существующие
    {
        "code": "first_quest_completed",
        "title": "Первая стезя",
        "description": "Выполните свой первый квест.",
        "icon_url": "🏅",
        "xp_bonus": 15,
    },
    {
        "code": "streak_3_days",
        "title": "Искра дисциплины",
        "description": "Выполняйте квесты 3 дня подряд.",
        "icon_url": "🔥",
        "xp_bonus": 30,
    },
    {
        "code": "streak_7_days",
        "title": "Пламя дисциплины",
        "description": "Выполняйте квесты 7 дней подряд.",
        "icon_url": "🔥",
        "xp_bonus": 50,
    },
    {
        "code": "level_5_reached",
        "title": "Искатель",
        "description": "Достигните 5-го уровня.",
        "icon_url": "⭐",
        "xp_bonus": 100,
    },
    {
        "code": "first_trial_survived",
        "title": "Упорство",
        "description": "Успешно завершите испытание.",
        "icon_url": "🛡️",
        "xp_bonus": 25,
    },
    {
        "code": "streak_30_days",
        "title": "Легендарная стойкость",
        "description": "Выполняйте квесты 30 дней подряд.",
        "icon_url": "🏆",
        "xp_bonus": 200,
    },
    {
        "code": "quests_10_completed",
        "title": "Начинающий герой",
        "description": "Выполните 10 квестов.",
        "icon_url": "📜",
        "xp_bonus": 30,
    },
    {
        "code": "quests_100_completed",
        "title": "Ветеран",
        "description": "Выполните 100 квестов.",
        "icon_url": "📜",
        "xp_bonus": 150,
    },
    {
        "code": "quests_1000_completed",
        "title": "Легенда",
        "description": "Выполните 1000 квестов.",
        "icon_url": "📜",
        "xp_bonus": 500,
    },
    {
        "code": "gold_1000_earned",
        "title": "Богач",
        "description": "Накопите 1000 монет (суммарно заработано, не потрачено).",
        "icon_url": "💰",
        "xp_bonus": 50,
    },
    {
        "code": "crystals_50_earned",
        "title": "Кристаллоносный",
        "description": "Накопите 50 кристаллов.",
        "icon_url": "💎",
        "xp_bonus": 100,
    },
    {
        "code": "first_purchase",
        "title": "Первый покупатель",
        "description": "Совершите первую покупку в магазине.",
        "icon_url": "🛒",
        "xp_bonus": 20,
    },
    {
        "code": "epic_gold_spent",
        "title": "Транжира",
        "description": "Потратьте в общей сложности 500 монет в магазине.",
        "icon_url": "💸",
        "xp_bonus": 60,
    },
    {
        "code": "all_subtasks_complete",
        "title": "Педант",
        "description": "Завершите родительскую задачу, закрыв все её подзадачи.",
        "icon_url": "📋",
        "xp_bonus": 40,
    },
    {
        "code": "redeem_3_trials",
        "title": "Искупитель",
        "description": "Выкупите 3 испытания за монеты.",
        "icon_url": "🔁",
        "xp_bonus": 35,
    },
]


# ── тестовые пользователи ─────────────────────────────────────────────────────

TEST_USERS = [
    {
        "username": "test_hero",
        "email": "test@lifequest.app",
        "password": "Test1234!",
        "display_name": "Тестовый Герой",
        "level": 3,
        "experience_points": 450,
        "coins": 80,
        "current_streak": 5,
    },
    {
        "username": "qa_tester",
        "email": "qa@lifequest.app",
        "password": "QaTest1234!",
        "display_name": "QA Тестировщик",
        "level": 1,
        "experience_points": 0,
        "coins": 50,
        "current_streak": 0,
    },
]


# ── тестовые задачи (создаются для test_hero) ─────────────────────────────────

def _make_tasks(user_id) -> list[dict]:
    now = datetime.now(timezone.utc)
    return [
        {
            "owner_id": user_id,
            "title": "Утренняя зарядка",
            "description": "15 минут зарядки каждое утро",
            "task_type": "daily",
            "effort_score": 3,
            "status": "active",
            "recurrence": "daily",
            "category": "health",
        },
        {
            "owner_id": user_id,
            "title": "Написать реферат по физике",
            "description": "Тема: квантовая механика, 10 страниц",
            "task_type": "regular",
            "effort_score": 8,
            "status": "active",
            "due_date": now + timedelta(days=3),
            "category": "study",
        },
        {
            "owner_id": user_id,
            "title": "Позвонить маме",
            "description": None,
            "task_type": "regular",
            "effort_score": 2,
            "status": "completed",
            "completed_at": now - timedelta(hours=2),
            "category": "family",
        },
        {
            "owner_id": user_id,
            "title": "Сдать лабораторную по химии",
            "description": "Просрочена на 10 дней",
            "task_type": "regular",
            "effort_score": 7,
            "status": "trial",
            "trial_since": now - timedelta(days=10),
            "due_date": now - timedelta(days=10),
            "category": "study",
        },
        {
            "owner_id": user_id,
            "title": "Выпить воду",
            "description": "8 стаканов в день",
            "task_type": "habit",
            "effort_score": 1,
            "status": "active",
            "recurrence": "daily",
            "category": "health",
        },
        {
            "owner_id": user_id,
            "title": "Прочитать главу книги",
            "description": "Атомные привычки — глава 3",
            "task_type": "regular",
            "effort_score": 4,
            "status": "active",
            "due_date": now + timedelta(days=1),
            "category": "study",
        },
    ]


# ── основная функция ──────────────────────────────────────────────────────────

async def seed_data():
    logger.info("Начинаем проверку и наполнение базы данных...")

    async with async_session_factory() as session:
        try:
            # ── достижения ────────────────────────────────────────────────────
            result = await session.execute(select(Achievement.code))
            existing_codes = set(result.scalars().all())

            new_achievements = [
                Achievement(**data)
                for data in INITIAL_ACHIEVEMENTS
                if data["code"] not in existing_codes
            ]
            if new_achievements:
                session.add_all(new_achievements)
                await session.commit()
                logger.info(f"Добавлено достижений: {len(new_achievements)}")
                for a in new_achievements:
                    logger.info(f"  + {a.title} ({a.code})")
            else:
                logger.info("Достижения уже существуют. Пропуск.")

            # ── тестовые пользователи ─────────────────────────────────────────
            for user_data in TEST_USERS:
                res = await session.execute(
                    select(User).where(User.username == user_data["username"])
                )
                existing = res.scalar_one_or_none()
                if existing:
                    logger.info(f"Пользователь «{user_data['username']}» уже существует. Пропуск.")
                    continue

                password = user_data.pop("password")
                new_user = User(
                    **user_data,
                    hashed_password=get_password_hash(password),
                )
                session.add(new_user)
                await session.flush()  # получаем new_user.id до commit

                # задачи только для test_hero
                if new_user.username == "test_hero":
                    tasks = [Task(**t) for t in _make_tasks(new_user.id)]
                    session.add_all(tasks)
                    logger.info(f"  + {len(tasks)} тестовых задач для «{new_user.username}»")

                logger.info(f"Создан пользователь: {new_user.username} (lvl {new_user.level})")

            await session.commit()
            logger.info("Наполнение базы завершено.")

        except Exception as e:
            await session.rollback()
            logger.error(f"Критическая ошибка: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())