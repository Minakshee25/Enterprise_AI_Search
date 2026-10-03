class JiraMCPClient:
    async def get_issue(
        self,
        issue_key: str,
    ) -> dict:
        ...

    async def search_issues(
        self,
        jql: str,
    ) -> dict:
        ...