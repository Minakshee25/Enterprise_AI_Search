from pathlib import Path

from fastmcp import Client


JIRA_SERVER_PATH = (
    Path(__file__)
    .resolve()
    .parents[2]
    / "mcp_servers"
    / "jira_server.py"
)


class JiraMCPClient:
    async def get_issue(
        self,
        issue_key: str,
    ) -> dict:

        async with Client(
            JIRA_SERVER_PATH
        ) as client:

            result = await client.call_tool(
                "get_jira_issue",
                {
                    "issue_key":
                        issue_key
                },
            )

            return result.data


    async def search_issues(
        self,
        jql: str,
        max_results: int = 10,
    ) -> dict:

        async with Client(
            JIRA_SERVER_PATH
        ) as client:

            result = await client.call_tool(
                "search_jira_issues",
                {
                    "jql": jql,
                    "max_results":
                        max_results,
                },
            )

            return result.data