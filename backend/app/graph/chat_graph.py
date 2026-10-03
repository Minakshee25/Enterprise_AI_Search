from langgraph.checkpoint.memory import (
    InMemorySaver,
)

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.graph.state import ChatState

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

from app.graph.nodes.language import (
    detect_input_language,
)

from app.graph.nodes.translation import (
    translate_answer,
    translate_to_english,
)

from app.graph.nodes.final_response import (
    final_response,
)

from app.graph.nodes.contextualize import (
    contextualize_query,
)

from app.graph.nodes.retrieve_knowledge import (
    retrieve_knowledge,
)

from app.graph.nodes.retrieval_grader import (
    grade_retrieval,
)

from app.graph.nodes.query_rewrite import (
    rewrite_query,
    after_retrieval_grade,
)
from app.graph.agents.web_agent import (
    web_agent,
)

def after_query_understanding(state):
    if state.get("route") == "simple":
        return "simple_response"

    return "detect_language"


def after_supervisor(state):
    route = state.get(
        "route",
        "fallback",
    )

    if route == "knowledge":
        return "contextualize_query"

    if route == "jira":
        return "jira_agent"

    if route == "web":
        return "web_agent"

    return "fallback"


def fallback(state):
    return {
        "final_answer": (
            "I can't handle that request "
            "through the currently available "
            "enterprise tools yet."
        )
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
    "detect_language",
    detect_input_language,
)

builder.add_node(
    "translate_to_english",
    translate_to_english,
)

builder.add_node(
    "supervisor",
    supervisor,
)

builder.add_edge(
    "web_agent",
    "translate_answer",
)

builder.add_node(
    "contextualize_query",
    contextualize_query,
)

builder.add_node(
    "retrieve_knowledge",
    retrieve_knowledge,
)

builder.add_node(
    "retrieval_grader",
    grade_retrieval,
)

builder.add_node(
    "rewrite_query",
    rewrite_query,
)

builder.add_node(
    "knowledge_agent",
    knowledge_agent,
)

builder.add_node(
    "fallback",
    fallback,
)

builder.add_node(
    "translate_answer",
    translate_answer,
)

builder.add_node(
    "final_response",
    final_response,
)


builder.add_edge(
    START,
    "query_understanding",
)


builder.add_conditional_edges(
    "query_understanding",
    after_query_understanding,
)


builder.add_edge(
    "detect_language",
    "translate_to_english",
)


builder.add_edge(
    "translate_to_english",
    "supervisor",
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
    "contextualize_query",
    "retrieve_knowledge",
)


builder.add_edge(
    "retrieve_knowledge",
    "retrieval_grader",
)


builder.add_conditional_edges(
    "retrieval_grader",
    after_retrieval_grade,
)


builder.add_edge(
    "rewrite_query",
    "retrieve_knowledge",
)


builder.add_edge(
    "knowledge_agent",
    "translate_answer",
)


builder.add_edge(
    "fallback",
    "translate_answer",
)


builder.add_edge(
    "translate_answer",
    "final_response",
)


builder.add_edge(
    "final_response",
    END,
)


chatbot = builder.compile(
    checkpointer=InMemorySaver()
)