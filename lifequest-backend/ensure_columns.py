"""
Ensure required columns exist before alembic/uvicorn start.
Runs raw SQL with IF NOT EXISTS — safe to re-run.
"""
import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Convert async URL to sync for psycopg2
db_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
db_url = db_url.replace("asyncpg://", "postgresql://")

COLUMNS = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_gold_earned INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_xp INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_gold INTEGER DEFAULT 0",
]

if db_url:
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        for sql in COLUMNS:
            try:
                cur.execute(sql)
                print(f"OK: {sql}")
            except Exception as e:
                print(f"SKIP: {e}")
        cur.close()
        conn.close()
        print("ensure_columns: done")
    except Exception as e:
        print(f"ensure_columns: could not connect: {e}")
else:
    print("ensure_columns: no DATABASE_URL, skipping")
