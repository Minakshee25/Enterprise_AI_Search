from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen2.5:3b"
)


def rewrite_query(state):
    query = state.get(
        "contextual_query",
        state["normalized_query"],
    )

    prompt = f"""
Rewrite this query for semantic search over
enterprise insurance policy documents.

Rules:
- Preserve the original intent.
- Use clear insurance terminology.
- Do not answer the query.
- Do not invent policy facts.
- Return only the rewritten search query.

Query:
{query}
"""

    response = llm.invoke(
        [
            HumanMessage(
                content=prompt
            )
        ]
    )

    retry_count = state.get(
        "retrieval_retry_count",
        0,
    )

    return {
        "contextual_query":
            response.content.strip(),

        "retrieval_retry_count":
            retry_count + 1,
    }

def after_retrieval_grade(state):
    quality = state.get(
        "retrieval_quality",
        "poor",
    )

    retries = state.get(
        "retrieval_retry_count",
        0,
    )

    if quality == "good":
        return "knowledge_agent"

    if retries < 1:
        return "rewrite_query"

    return "fallback"