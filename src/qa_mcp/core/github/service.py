from qa_mcp.infrastructure.github.client import (
    GitHubClient,
)

from qa_mcp.models.schemas import (
    GitHubIssue,
    GitHubPullRequest,
    GitHubRepository,
)


class GitHubService:
    """Business service for read-only GitHub operations."""

    def __init__(
        self,
        client: GitHubClient,
    ):
        self.client = client

    def get_repository(
        self,
        owner: str,
        repository: str,
    ) -> GitHubRepository:

        self._validate_owner(
            owner
        )

        self._validate_repository(
            repository
        )

        return self.client.get_repository(
            owner=owner,
            repository=repository,
        )

    def get_issue(
        self,
        owner: str,
        repository: str,
        issue_number: int,
    ) -> GitHubIssue:

        self._validate_owner(
            owner
        )

        self._validate_repository(
            repository
        )

        if issue_number <= 0:
            raise ValueError(
                "Issue number must be greater than zero"
            )

        return self.client.get_issue(
            owner=owner,
            repository=repository,
            issue_number=issue_number,
        )

    def get_pull_request(
        self,
        owner: str,
        repository: str,
        pull_number: int,
    ) -> GitHubPullRequest:

        self._validate_owner(
            owner
        )

        self._validate_repository(
            repository
        )

        if pull_number <= 0:
            raise ValueError(
                "Pull request number must be greater than zero"
            )

        return self.client.get_pull_request(
            owner=owner,
            repository=repository,
            pull_number=pull_number,
        )

    def search_issues(
        self,
        query: str,
        max_results: int = 50,
    ) -> list[GitHubIssue]:

        if not query.strip():
            raise ValueError(
                "Search query cannot be empty"
            )

        if max_results <= 0:
            raise ValueError(
                "max_results must be greater than zero"
            )

        return self.client.search_issues(
            query=query,
            max_results=max_results,
        )

    @staticmethod
    def _validate_owner(
        owner: str,
    ) -> None:

        if not owner.strip():
            raise ValueError(
                "GitHub owner cannot be empty"
            )

    @staticmethod
    def _validate_repository(
        repository: str,
    ) -> None:

        if not repository.strip():
            raise ValueError(
                "GitHub repository cannot be empty"
            )