import asyncio
import logging
from sqlalchemy import select

from app.core.database import async_session_factory
from app.models.achievement import Achievement

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s [%(name)s] %(message)s",
)
logger = logging.getLogger("seed")

# каталог достижений для MVP
INITIAL_ACHIEVEMENTS = [
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
    }
]


async def seed_data():
    """Асинхронная функция для наполнения базы стартовыми данными."""
    logger.info("Начинаем проверку и сидирование базы данных...")
    
    async with async_session_factory() as session:
        try:
            result = await session.execute(select(Achievement.code))
            existing_codes = set(result.scalars().all())

            new_achievements = []
            
            for ach_data in INITIAL_ACHIEVEMENTS:
                if ach_data["code"] not in existing_codes:
                    new_achievement = Achievement(**ach_data)
                    new_achievements.append(new_achievement)

            if new_achievements:
                session.add_all(new_achievements)
                await session.commit()
                
                logger.info(f"Успешно добавлено новых достижений: {len(new_achievements)}")
                for ach in new_achievements:
                    logger.info(f"  + {ach.title} ({ach.code})")
            else:
                logger.info("База данных уже содержит все базовые достижения. Пропуск.")

        except Exception as e:
            await session.rollback()
            logger.error(f"Критическая ошибка при сидировании: {e}")
            raise


if __name__ == "__main__":
    # event loop
    asyncio.run(seed_data())