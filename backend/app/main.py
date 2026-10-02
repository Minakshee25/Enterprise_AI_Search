# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from sqlalchemy import text

from app.db.database import engine

app = FastAPI(
    title="Knowledge Hub Assistant API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


app.include_router(
    chat_router,
    prefix="/api/v1",
    tags=["chat"],
)

@app.get("/db-health")
async def database_health():
    async with engine.connect() as connection:
        result = await connection.execute(
            text("SELECT 1")
        )

        return {
            "database": "ok",
            "result": result.scalar(),
        }