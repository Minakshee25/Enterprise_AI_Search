from langchain_core.messages import (
    HumanMessage,
)
from langchain_ollama import ChatOllama
from app.config import settings


llm = ChatOllama(
    model="qwen2.5:3b",
    base_url=settings.ollama_base_url,
)


def contextualize_query(state):
    messages = state.get(
        "messages",
        [],
    )

    query = state[
        "normalized_query"
    ]

    if len(messages) <= 1:
        return {
            "contextual_query": query
        }

    history = []

    for message in messages[-6:]:
        content = getattr(
            message,
            "content",
            "",
        )

        if isinstance(content, str):
            history.append(content)

    prompt = f"""
        Rewrite the latest user query as a standalone
        enterprise search query using relevant conversation
        context.

        Rules:
        - Preserve the user's meaning.
        - Do not answer the question.
        - Do not add facts.
        - Return only the rewritten query.
        - If the latest query is already standalone,
        return it unchanged.

        Conversation:
        {chr(10).join(history)}

        Latest query:
        {query}
        """

    response = llm.invoke(
        [
            HumanMessage(
                content=prompt
            )
        ]
    )

    return {
        "contextual_query":
            response.content.strip()
    }