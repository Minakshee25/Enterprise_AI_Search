from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)



class Settings(BaseSettings):
    database_url: str

    entra_tenant_id: str
    entra_api_client_id: str

    milvus_uri: str
    redis_url: str

    tavily_api_key: str | None = None

    # ollama_base_url: str = (
    #     "http://localhost:11434"
    # )

    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:3b"
    llm_base_url: str = "http://localhost:11434"
    llm_api_key: str = "dummy"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()