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
        f"{JIRA_BASE_URL}"
        f"/rest/api/3/issue/{issue_key}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            auth=jira_auth(),
            headers={
                "Accept":
                    "application/json"
            },
            params={
                "fields":
                    "summary,status,"
                    "issuetype,priority,"
                    "assignee,reporter,"
                    "updated,description"
            },
        )

        response.raise_for_status()

        issue = response.json()

    fields = issue.get(
        "fields",
        {},
    )

    return {
        "key":
            issue.get("key"),

        "summary":
            fields.get("summary"),

        "status":
            (
                fields
                .get("status", {})
                .get("name")
            ),

        "issue_type":
            (
                fields
                .get("issuetype", {})
                .get("name")
            ),

        "priority":
            (
                fields
                .get("priority", {})
                .get("name")
                if fields.get(
                    "priority"
                )
                else None
            ),

        "assignee":
            (
                fields
                .get("assignee", {})
                .get("displayName")
                if fields.get(
                    "assignee"
                )
                else None
            ),

        "updated":
            fields.get("updated"),

        "description":
            fields.get(
                "description"
            ),
    }

@mcp.tool()
async def search_jira_issues(
    jql: str,
    max_results: int = 10,
) -> dict:

    url = (
        f"{JIRA_BASE_URL}"
        "/rest/api/3/search/jql"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            auth=jira_auth(),
            headers={
                "Accept":
                    "application/json"
            },
            params={
                "jql":
                    jql,

                "maxResults":
                    max_results,

                "fields":
                    "summary,status,"
                    "priority,updated",
            },
        )

        response.raise_for_status()

        data = response.json()

    issues = []

    for issue in data.get(
        "issues",
        [],
    ):
        fields = issue.get(
            "fields",
            {},
        )

        issues.append(
            {
                "key":
                    issue.get("key"),

                "summary":
                    fields.get(
                        "summary"
                    ),

                "status":
                    (
                        fields
                        .get("status", {})
                        .get("name")
                    ),

                "priority":
                    (
                        fields
                        .get(
                            "priority",
                            {},
                        )
                        .get("name")
                        if fields.get(
                            "priority"
                        )
                        else None
                    ),

                "updated":
                    fields.get(
                        "updated"
                    ),
            }
        )

    return {
        "issues": issues
    }
if __name__ == "__main__":
    mcp.run()