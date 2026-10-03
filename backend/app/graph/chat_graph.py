from langgraph.checkpoint.memory import (
    InMemorySaver,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.graph.agents.knowledge_agent import (
    knowledge_agent,
)
from app.graph.nodes.query_understanding import (
    understand_query,
)
from app.graph.nodes.simple_response import (
    simple_response,
)
from app.graph.nodes.supervisor import (
    supervisor,
)
from app.graph.state import ChatState


def after_query_understanding(state):
    if state.get("route") == "simple":
        return "simple_response"

    return "supervisor"


def after_supervisor(state):
    route = state.get(
        "route",
        "fallback",
    )

    if route == "knowledge":
        return "knowledge_agent"

    return "fallback"


def fallback(state):
    from langchain_core.messages import (
        AIMessage,
    )

    answer = (
        "I can't handle that request "
        "through the currently available "
        "enterprise tools yet."
    )

    return {
        "messages": [
            AIMessage(
                content=answer
            )
        ],
        "final_answer": answer,
    }


builder = StateGraph(ChatState)

builder.add_node(
    "query_understanding",
    understand_query,
)

builder.add_node(
    "simple_response",
    simple_response,
)

builder.add_node(
    "supervisor",
    supervisor,
)

builder.add_node(
    "knowledge_agent",
    knowledge_agent,
)

builder.add_node(
    "fallback",
    fallback,
)

builder.add_edge(
    START,
    "query_understanding",
)

builder.add_conditional_edges(
    "query_understanding",
    after_query_understanding,
)

builder.add_conditional_edges(
    "supervisor",
    after_supervisor,
)

builder.add_edge(
    "simple_response",
    END,
)

builder.add_edge(
    "knowledge_agent",
    END,
)

builder.add_edge(
    "fallback",
    END,
)

chatbot = builder.compile(
    checkpointer=InMemorySaver()
)