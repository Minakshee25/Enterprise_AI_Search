import redis.asyncio as redis

from app.config import settings


redis_client: redis.Redis | None = None


async def connect_redis():
    global redis_client

    redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )

    await redis_client.ping()


async def close_redis():
    global redis_client

    if redis_client is not None:
        await redis_client.aclose()

        redis_client = None


def get_redis() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError(
            "Redis has not been initialized"
        )

    return redis_client