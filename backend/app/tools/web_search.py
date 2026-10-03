from tavily import TavilyClient

from app.config import settings


def get_tavily_client() -> TavilyClient:
    if not settings.tavily_api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is not configured"
        )

    return TavilyClient(
        api_key=settings.tavily_api_key
    )


def search_web(
    query: str,
    max_results: int = 5,
) -> list[dict]:

    client = get_tavily_client()

    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced",
    )

    results = []

    for item in response.get(
        "results",
        [],
    ):
        results.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content"),
                "score": item.get("score"),
            }
        )

    return results