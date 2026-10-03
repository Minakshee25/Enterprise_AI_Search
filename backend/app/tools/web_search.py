import os

from tavily import TavilyClient


client = TavilyClient(
    api_key=os.environ["TAVILY_API_KEY"]
)


def search_web(
    query: str,
    max_results: int = 5,
) -> list[dict]:

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