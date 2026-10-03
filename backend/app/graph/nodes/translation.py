from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from app.config import settings


translation_llm = ChatOllama(
    model="qwen2.5:3b",
    base_url=settings.ollama_base_url
)


def translate_to_english(state):
    if not state.get(
        "requires_translation",
        False,
    ):
        return {
            "normalized_query":
                state["original_query"]
        }

    query = state["original_query"]

    prompt = f"""
Translate the following user message into English.

Rules:
- Preserve the exact meaning.
- Do not answer the question.
- Do not explain anything.
- Return only the translated text.

Message:
{query}
"""

    response = translation_llm.invoke(
        [
            HumanMessage(
                content=prompt
            )
        ]
    )

    return {
        "normalized_query":
            response.content.strip()
    }


def translate_answer(state):
    language = state.get(
        "language",
        "en",
    )

    if language == "en":
        return {}

    answer = state["final_answer"]

    prompt = f"""
Translate the following answer into language code "{language}".

Rules:
- Preserve meaning exactly.
- Preserve filenames.
- Preserve policy names.
- Preserve numbers and monetary values.
- Preserve Jira IDs.
- Do not add new information.
- Return only the translated answer.

Answer:
{answer}
"""

    response = translation_llm.invoke(
        [
            HumanMessage(
                content=prompt
            )
        ]
    )

    return {
        "final_answer":
            response.content.strip()
    }