from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "lifequest",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.celery_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        # Сброс стриков — 00:05 UTC ежедневно
        "reset-broken-streaks": {
            "task": "app.tasks.celery_tasks.reset_broken_streaks",
            "schedule": crontab(hour=0, minute=5),
            "options": {"expires": 3600},
        },
        # Перевод просроченных задач в Испытание — каждые 10 минут
        "transition-overdue-tasks": {
            "task": "app.tasks.celery_tasks.transition_overdue_tasks_to_trial",
            "schedule": 600.0,
            "options": {"expires": 3600},
        },
        # Сброс weekly_xp — каждый понедельник 00:01 UTC (FR-7.3)
        "reset-weekly-xp": {
            "task": "app.tasks.celery_tasks.reset_weekly_xp",
            "schedule": crontab(hour=0, minute=1, day_of_week=1),
            "options": {"expires": 3600},
        },
    },
)