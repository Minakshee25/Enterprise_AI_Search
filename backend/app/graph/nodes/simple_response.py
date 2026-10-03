from langchain_core.messages import AIMessage


def simple_response(state):
    query = (
        state["original_query"]
        .strip()
        .lower()
    )

    responses = {
        "hi": "Hi! How can I help?",
        "hello": "Hello! How can I help?",
        "hey": "Hey! How can I help?",
        "thanks": "You're welcome.",
        "thank you": "You're welcome.",
        "bye": "Goodbye!",

        "hej": "Hej! Hvordan kan jeg hjælpe?",
        "hei": "Hei! Hvordan kan jeg hjelpe?",
        "tak": "Velbekomme.",
        "takk": "Bare hyggelig.",
    }
    answer = responses.get(
        query,
        "How can I help?"
    )

    return {
        "messages": [
            AIMessage(
                content=answer
            )
        ],
        "final_answer": answer,
    }