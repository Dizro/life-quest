"""конфигурация Celery — брокер задач на базе Redis."""

import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "lifequest",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "transition-overdue-tasks-daily": {
            "task": "tasks.transition_overdue_tasks_to_trial",
            "schedule": crontab(hour=0, minute=1),
        },
        "reset-broken-streaks-daily": {
            "task": "tasks.reset_broken_streaks",
            "schedule": crontab(hour=0, minute=5),
        },
    }
)

celery_app.conf.beat_schedule = {
    # Существующие задачи
    'transition-overdue-tasks': {
        'task': 'tasks.transition_overdue_tasks_to_trial',
        'schedule': crontab(minute=1, hour=0),  # 00:01 каждый день
    },
    'reset-streaks': {
        'task': 'tasks.reset_broken_streaks',
        'schedule': crontab(minute=5, hour=0),  # 00:05 каждый день
    },
    
    # ➕ Новая задача: проверка дедлайнов (каждый час)
    'check-deadlines': {
        'task': 'tasks.check_upcoming_deadlines',
        'schedule': crontab(minute=0),  # каждый час в 00 минут
        'options': {
            'expires': 300,  # задача устаревает через 5 минут
        }
    },
    'reset-daily-limits': {
        'task': 'tasks.reset_daily_limits',
        'schedule': crontab(minute=0, hour=0),  # каждый день в 00:00 UTC
        'options': {
            'expires': 3600,  # задача устаревает через час
        }
    },
}

# автоматическое обнаружение задач из модуля app.tasks.celery_tasks
celery_app.autodiscover_tasks(["app.tasks"], related_name="celery_tasks")

