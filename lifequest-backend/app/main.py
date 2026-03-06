from fastapi import FastAPI

app = FastAPI(
    title="LifeQuest API",
    description="Backend for Gamified Task Tracker",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "LifeQuest API is running"}
