from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from uuid import UUID

from app.auth.user import get_current_user
from app.api.chat import router as chat_router
from app.db.database import (
    close_db,
    connect_db,
    get_pool,
)
from app.cache.redis import (
    close_redis,
    connect_redis,
)
from app.cache.redis import get_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await connect_redis()

    yield

    await close_redis()
    await close_db()



app = FastAPI(
    title="AIassistant API",
    version="0.1.0",
    lifespan=lifespan,
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

@app.get("/me")
async def me(
    user_id: UUID = Depends(get_current_user),
):
    return {
        "user_id": user_id
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/db-health")
async def database_health():

    db = get_pool()

    result = await db.fetchval(
        "SELECT 1"
    )

    return {
        "database": "ok",
        "result": result,
    }

@app.get("/redis-health")
async def redis_health():
    redis = get_redis()

    result = await redis.ping()

    return {
        "redis": "ok",
        "result": result,
    }

app.include_router(
    chat_router,
    prefix="/api/v1",
    tags=["chat"],
)