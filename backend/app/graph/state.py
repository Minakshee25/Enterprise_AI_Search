from langgraph.graph.message import add_messages

from typing import Annotated, Literal, TypedDict
from langchain_core.messages import BaseMessage

class ChatState(TypedDict, total=False):
    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    original_query: str
    normalized_query: str

    language: str
    requires_translation: bool

    intent: str

    route: Literal[
        "simple",
        "knowledge",
        "jira",
        "web",
        "fallback",
    ]

    retrieved_chunks: list[dict]

    final_answer: str

    error: str | None