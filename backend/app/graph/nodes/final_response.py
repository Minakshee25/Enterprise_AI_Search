from langchain_core.messages import (
    AIMessage,
)


def final_response(state):
    answer = state.get(
        "final_answer",
        "",
    )

    return {
        "messages": [
            AIMessage(
                content=answer
            )
        ]
    }