from app.retrieval.search import (
    search_policy_chunks,
)


def retrieve_enterprise_knowledge(
    query: str,
    top_k: int = 5,
) -> list[dict]:

    return search_policy_chunks(
        query=query,
        limit=top_k,
    )