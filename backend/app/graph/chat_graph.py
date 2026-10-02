# backend/app/graph/chat_graph.py

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


llm = ChatOllama(
    model="qwen2.5:7b"
)


def chat_node(state: ChatState):
    messages = state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }


checkpointer = InMemorySaver()

graph_builder = StateGraph(ChatState)

graph_builder.add_node(
    "chat_node",
    chat_node
)

graph_builder.add_edge(
    START,
    "chat_node"
)

graph_builder.add_edge(
    "chat_node",
    END
)

chatbot = graph_builder.compile(
    checkpointer=checkpointer
)
