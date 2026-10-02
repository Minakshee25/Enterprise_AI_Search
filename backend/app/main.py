from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.db.database import (
    close_db,
    connect_db,
    get_pool,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()

    yield

    await close_db()


app = FastAPI(
    title="Knowledge Hub Assistant API",
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


app.include_router(
    chat_router,
    prefix="/api/v1",
    tags=["chat"],
)