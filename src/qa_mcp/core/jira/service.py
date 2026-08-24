from qa_mcp.infrastructure.jira.client import JiraClient
from qa_mcp.models.schemas import (
    JiraIssue,
    JiraSearchResult,
)


class JiraService:
    """Business-facing service for Jira operations."""

    def __init__(
        self,
        client: JiraClient,
    ):
        self.client = client

    def get_issue(
        self,
        issue_key: str,
    ) -> JiraIssue:
        """Retrieve a Jira issue by key."""

        if not issue_key.strip():
            raise ValueError(
                "Jira issue key cannot be empty"
            )

        return self.client.get_issue(
            issue_key.strip()
        )

    def search_issues(
        self,
        jql: str,
        max_results: int = 50,
    ) -> JiraSearchResult:
        """Search Jira issues using JQL."""

        if not jql.strip():
            raise ValueError(
                "Jira JQL cannot be empty"
            )

        if max_results < 1:
            raise ValueError(
                "max_results must be greater than 0"
            )

        return self.client.search_issues(
            jql.strip(),
            max_results=max_results,
        )