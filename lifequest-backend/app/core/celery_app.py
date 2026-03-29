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

# автоматическое обнаружение задач из модуля app.tasks.celery_tasks
celery_app.autodiscover_tasks(["app.tasks"], related_name="celery_tasks")
