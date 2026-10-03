import hashlib
import json

from app.cache.redis import (
    get_redis,
)


CACHE_TTL_SECONDS = 300


def build_cache_key(
    query: str,
    top_k: int,
) -> str:

    raw = (
        f"{query.strip().lower()}::{top_k}"
    )

    digest = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()

    return (
        f"retrieval:{digest}"
    )


async def get_cached_retrieval(
    query: str,
    top_k: int,
) -> list[dict] | None:

    redis = get_redis()

    key = build_cache_key(
        query,
        top_k,
    )

    value = await redis.get(key)

    if value is None:
        return None

    return json.loads(value)


async def cache_retrieval(
    query: str,
    top_k: int,
    results: list[dict],
) -> None:

    redis = get_redis()

    key = build_cache_key(
        query,
        top_k,
    )

    await redis.setex(
        key,
        CACHE_TTL_SECONDS,
        json.dumps(results),
    )