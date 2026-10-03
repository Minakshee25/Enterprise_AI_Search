from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama


router_llm = ChatOllama(
    model="qwen2.5:3b"
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

    route = (
        response.content
        .strip()
        .lower()
    )

    allowed = {
        "knowledge",
        "jira",
        "web",
        "fallback",
    }

    if route not in allowed:
        route = "fallback"

    return {
        "route": route
    }