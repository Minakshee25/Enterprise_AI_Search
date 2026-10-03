from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama


small_llm = ChatOllama(
    model="qwen2.5:3b"
)


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
        user_messages[-1].content.strip()
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

    return {
        "original_query": query,
        "normalized_query": query,
        "language": "en",
        "intent": "unknown",
    }