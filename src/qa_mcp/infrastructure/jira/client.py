from abc import ABC, abstractmethod

from qa_mcp.models.schemas import (
    JiraIssue,
    JiraSearchResult,
)


class JiraClient(ABC):
    """Abstract Jira client."""

    @abstractmethod
    def get_issue(
        self,
        issue_key: str,
    ) -> JiraIssue:
        """Retrieve a Jira issue by key."""

        raise NotImplementedError

    @abstractmethod
    def search_issues(
        self,
        jql: str,
        max_results: int = 50,
    ) -> JiraSearchResult:
        """Search Jira issues using JQL."""

        raise NotImplementedError