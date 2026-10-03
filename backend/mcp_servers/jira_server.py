import os

import httpx
from fastmcp import FastMCP


mcp = FastMCP("jira-readonly")


JIRA_BASE_URL = os.environ["JIRA_BASE_URL"]
JIRA_EMAIL = os.environ["JIRA_EMAIL"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]


def jira_auth():
    return (
        JIRA_EMAIL,
        JIRA_API_TOKEN,
    )


@mcp.tool()
async def get_jira_issue(
    issue_key: str,
) -> dict:
    url = (
        f"{JIRA_BASE_URL}/rest/api/3/"
        f"issue/{issue_key}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            auth=jira_auth(),
            headers={
                "Accept": "application/json"
            },
        )

        response.raise_for_status()

        return response.json()


@mcp.tool()
async def search_jira_issues(
    jql: str,
    max_results: int = 10,
) -> dict:
    url = (
        f"{JIRA_BASE_URL}/rest/api/3/search"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            auth=jira_auth(),
            params={
                "jql": jql,
                "maxResults": max_results,
            },
            headers={
                "Accept": "application/json"
            },
        )

        response.raise_for_status()

        return response.json()


if __name__ == "__main__":
    mcp.run()