from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
from langchain_ollama import ChatOllama

from app.tools.knowledge import (
    retrieve_enterprise_knowledge,
)


llm = ChatOllama(
    model="qwen2.5:3b"
)


def knowledge_agent(state):
    chunks = state.get(
    "retrieved_chunks",
    [],
)

    if not chunks:
        answer = (
            "I could not find enough "
            "information in the available "
            "enterprise documents."
        )

        return {
            "retrieved_chunks": [],
            "final_answer": answer,
        }

    context = "\n\n".join(
        [
            (
                f"Source {index}\n"
                f"File: {chunk['filename']}\n"
                f"Page: {chunk['page_number']}\n"
                f"Content:\n{chunk['text']}"
            )
            for index, chunk
            in enumerate(
                chunks,
                start=1,
            )
        ]
    )

    system_message = SystemMessage(
        content=(
            "You are an enterprise insurance "
            "knowledge assistant. "
            "Use only the supplied context. "
            "If the context does not support "
            "the answer, say so. "
            "Do not invent policy details.\n\n"
            f"{context}"
        )
    )

    response = llm.invoke(
        [
            system_message,
            HumanMessage(
                content=query
            ),
        ]
    )

    return {
        "retrieved_chunks": chunks,
        "final_answer": response.content,
    }