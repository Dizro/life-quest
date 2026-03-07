# 🎮 LifeQuest

Геймифицированный трекер задач в формате RPG. Каждая задача — квест, за выполнение которого герой получает опыт, монеты и достижения.

> ⚠️ Проект в активной разработке — это MVP первого спринта. Функционал расширяется с каждым спринтом.

## Стек

**Бэкенд:** FastAPI · PostgreSQL 15 · Redis · Celery · SQLAlchemy 2.0 · Alembic · Docker

## Быстрый старт

```bash
# 1. Клонировать
git clone https://codelab.tpu.ru/egk17/lifequest.git
cd lifequest/lifequest-backend

# 2. Создать .env
cp .env.example .env

# 3. Поднять всё
docker-compose up --build

# 4. Открыть API docs
# http://localhost:8000/docs
```

Без Docker:

```bash
cd lifequest-backend
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Проверка

```bash
curl http://localhost:8000/health
# {"status":"ok","message":"LifeQuest API работает"}
```