from qa_mcp.models.schemas import (
    JiraIssue,
    JiraSearchResult,
)

from qa_mcp.infrastructure.jira.client import (
    JiraClient,
)


class MockJiraClient(JiraClient):
    """In-memory Jira client for testing."""

    def __init__(
        self,
        issues: list[JiraIssue] | None = None,
    ):
        self._issues = {
            issue.key: issue
            for issue in (
                issues or []
            )
        }

    def get_issue(
        self,
        issue_key: str,
    ) -> JiraIssue:

        issue = self._issues.get(
            issue_key
        )

        if issue is None:
            raise ValueError(
                f"Jira issue not found: "
                f"{issue_key}"
            )

        return issue

    def search_issues(
        self,
        jql: str,
        max_results: int = 50,
    ) -> JiraSearchResult:

        # Initial mock behavior:
        # return all configured issues.
        # Real JQL parsing belongs to the
        # Jira Cloud implementation.

        issues = list(
            self._issues.values()
        )[:max_results]

        return JiraSearchResult(
            issues=issues,
            total=len(issues),
        )