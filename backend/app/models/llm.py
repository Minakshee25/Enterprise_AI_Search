from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app.config import settings


def get_llm():

    if settings.llm_provider == "ollama":
        return ChatOllama(
            model=settings.llm_model,
            base_url=settings.llm_base_url,
        )

    if settings.llm_provider == "vllm":
        return ChatOpenAI(
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )

    raise ValueError(
        f"Unknown LLM provider: "
        f"{settings.llm_provider}"
    )