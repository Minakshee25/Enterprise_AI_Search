from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
from langchain_ollama import ChatOllama

from app.tools.web_search import (
    search_web,
)
from app.config import settings


llm = ChatOllama(
    model="qwen2.5:3b",
    base_url=settings.ollama_base_url,
)


def web_agent(state):
    query = state.get(
        "contextual_query",
        state["normalized_query"],
    )

    results = search_web(
        query=query,
        max_results=5,
    )

    if not results:
        return {
            "web_result": [],
            "final_answer": (
                "I could not find reliable "
                "public information for that request."
            ),
        }

    context_parts = []

    sources = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        context_parts.append(
            (
                f"Source {index}\n"
                f"Title: {result['title']}\n"
                f"URL: {result['url']}\n"
                f"Content:\n"
                f"{result['content']}"
            )
        )

        sources.append(
            {
                "type": "web",
                "title": result["title"],
                "url": result["url"],
            }
        )

    context = "\n\n".join(
        context_parts
    )

    system_message = SystemMessage(
        content=(
            "You are an enterprise research assistant. "
            "Answer the user using only the supplied "
            "web search evidence. "
            "Do not invent facts. "
            "When sources disagree, state that clearly."
        )
    )

    response = llm.invoke(
        [
            system_message,
            HumanMessage(
                content=(
                    f"Question:\n{query}\n\n"
                    f"Web evidence:\n{context}"
                )
            ),
        ]
    )

    return {
        "web_result": results,
        "sources": sources,
        "final_answer": response.content,
    }