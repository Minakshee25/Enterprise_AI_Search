from app.cache.retrieval_cache import (
    cache_retrieval,
    get_cached_retrieval,
)
from app.tools.knowledge import (
    retrieve_enterprise_knowledge,
)
from langsmith import traceable

@traceable(
    name="retrieve_knowledge"
)

async def retrieve_knowledge(state):
    query = state.get(
        "contextual_query",
        state["normalized_query"],
    )

    top_k = 5

    cached = await get_cached_retrieval(
        query=query,
        top_k=top_k,
    )

    if cached is not None:
        return {
            "retrieved_chunks": cached,
        }

    chunks = (
        retrieve_enterprise_knowledge(
            query=query,
            top_k=top_k,
        )
    )

    await cache_retrieval(
        query=query,
        top_k=top_k,
        results=chunks,
    )

    return {
        "retrieved_chunks": chunks,
    }