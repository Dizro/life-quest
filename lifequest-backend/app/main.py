import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api.v1.router import api_router
from app.core.database import engine

logger = logging.getLogger(__name__)

ENSURE_COLUMNS = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_gold_earned INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_xp INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_gold INTEGER DEFAULT 0",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        for sql in ENSURE_COLUMNS:
            try:
                await conn.execute(text(sql))
            except Exception as e:
                logger.warning(f"Column check: {e}")
    yield


app = FastAPI(
    lifespan=lifespan,
    title="LifeQuest API",
    description="Геймифицированный трекер задач с ИИ-наставником Фарриксом",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dizro.github.io",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "service": "lifequest-api"}