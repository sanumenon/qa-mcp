from abc import ABC, abstractmethod

from qa_mcp.models.schemas import (
    GitHubIssue,
    GitHubPullRequest,
    GitHubRepository,
)


class GitHubClient(ABC):
    """Abstract GitHub client."""

    @abstractmethod
    def get_repository(
        self,
        owner: str,
        repository: str,
    ) -> GitHubRepository:
        """Retrieve a GitHub repository."""

        raise NotImplementedError

    @abstractmethod
    def get_issue(
        self,
        owner: str,
        repository: str,
        issue_number: int,
    ) -> GitHubIssue:
        """Retrieve a GitHub issue."""

        raise NotImplementedError

    @abstractmethod
    def get_pull_request(
        self,
        owner: str,
        repository: str,
        pull_number: int,
    ) -> GitHubPullRequest:
        """Retrieve a GitHub pull request."""

        raise NotImplementedError

    @abstractmethod
    def search_issues(
        self,
        query: str,
        max_results: int = 50,
    ) -> list[GitHubIssue]:
        """Search GitHub issues."""

        raise NotImplementedError