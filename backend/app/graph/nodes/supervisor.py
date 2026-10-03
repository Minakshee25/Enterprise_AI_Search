from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from app.config import settings

router_llm = ChatOllama(
    model="qwen2.5:3b",
    base_url=settings.ollama_base_url
)


def supervisor(state):
    query = state["normalized_query"]

    prompt = f"""
Classify the following enterprise assistant query.

Allowed routes:
- knowledge
- jira
- web
- fallback

Use:
knowledge = internal insurance policy or enterprise knowledge question
jira = question about Jira tickets/issues/status
web = question requiring current public information
fallback = anything else

Return only one route name.

Query:
{query}
"""

    response = router_llm.invoke(
        [
            HumanMessage(
                content=prompt
            )
        ]
    )

    raw_route = (
        response.content
        .strip()
        .lower()
    )

    route = "fallback"

    if "knowledge" in raw_route:
        route = "knowledge"

    elif "jira" in raw_route:
        route = "jira"

    elif "web" in raw_route:
        route = "web"

    elif "fallback" in raw_route:
        route = "fallback"

    print(
        f"[supervisor] "
        f"query={query!r}, "
        f"raw={raw_route!r}, "
        f"route={route!r}"
    )

    return {
        "route": route
    }