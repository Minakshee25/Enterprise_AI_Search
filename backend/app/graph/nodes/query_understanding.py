from langchain_core.messages import HumanMessage


SIMPLE_MESSAGES = {
    "hi",
    "hello",
    "hey",
    "thanks",
    "thank you",
    "good morning",
    "good afternoon",
    "good evening",
    "bye",

    # Danish / Norwegian / Swedish basics
    "hej",
    "hei",
    "takk",
    "tak",
}


def understand_query(state):
    messages = state["messages"]

    user_messages = [
        message
        for message in messages
        if isinstance(
            message,
            HumanMessage,
        )
    ]

    query = (
        user_messages[-1]
        .content
        .strip()
    )

    normalized = query.lower()

    if normalized in SIMPLE_MESSAGES:
        return {
            "original_query": query,
            "normalized_query": query,
            "language": "en",
            "intent": "simple",
            "route": "simple",
        }

    # IMPORTANT:
    # Explicitly overwrite route from the
    # previous LangGraph turn.
    return {
        "original_query": query,
        "normalized_query": query,
        "language": "en",
        "intent": "unknown",
        "route": "fallback",
    }