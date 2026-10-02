import asyncpg

from app.config import settings


pool: asyncpg.Pool | None = None


async def connect_db():
    global pool

    pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=1,
        max_size=5,
    )


async def close_db():
    global pool

    if pool is not None:
        await pool.close()
        pool = None


def get_pool() -> asyncpg.Pool:
    if pool is None:
        raise RuntimeError("Database pool has not been initialized")

    return pool