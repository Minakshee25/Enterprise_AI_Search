from app.tools.knowledge import (
    retrieve_enterprise_knowledge,
)


def retrieve_knowledge(state):
    query = state.get(
        "contextual_query",
        state["normalized_query"],
    )

    chunks = (
        retrieve_enterprise_knowledge(
            query=query,
            top_k=5,
        )
    )

    return {
        "retrieved_chunks": chunks,
    }