from qa_mcp.infrastructure.github.client import (
    GitHubClient,
)

from qa_mcp.models.schemas import (
    GitHubIssue,
    GitHubPullRequest,
    GitHubRepository,
)


class MockGitHubClient(GitHubClient):
    """Deterministic GitHub client for local development."""

    def get_repository(
        self,
        owner: str,
        repository: str,
    ) -> GitHubRepository:
        return GitHubRepository(
            full_name=f"{owner}/{repository}",
            name=repository,
            owner=owner,
            description=(
                "Mock GitHub repository"
            ),
            url=(
                f"https://github.com/"
                f"{owner}/{repository}"
            ),
            default_branch="main",
        )

    def get_issue(
        self,
        owner: str,
        repository: str,
        issue_number: int,
    ) -> GitHubIssue:
        return GitHubIssue(
            number=issue_number,
            title=(
                f"Mock GitHub Issue "
                f"#{issue_number}"
            ),
            state="open",
            body=(
                "Mock GitHub issue "
                "description."
            ),
            url=(
                f"https://github.com/"
                f"{owner}/{repository}"
                f"/issues/{issue_number}"
            ),
            repository=(
                f"{owner}/{repository}"
            ),
            author="mock-user",
        )

    def get_pull_request(
        self,
        owner: str,
        repository: str,
        pull_number: int,
    ) -> GitHubPullRequest:
        return GitHubPullRequest(
            number=pull_number,
            title=(
                f"Mock Pull Request "
                f"#{pull_number}"
            ),
            state="open",
            body=(
                "Mock GitHub pull request "
                "description."
            ),
            url=(
                f"https://github.com/"
                f"{owner}/{repository}"
                f"/pull/{pull_number}"
            ),
            repository=(
                f"{owner}/{repository}"
            ),
            author="mock-user",
            head_branch="feature/mock",
            base_branch="main",
        )

    def search_issues(
        self,
        query: str,
        max_results: int = 50,
    ) -> list[GitHubIssue]:

        issues = [
            GitHubIssue(
                number=1,
                title="Mock password reset issue",
                state="open",
                body=(
                    "Mock issue matching "
                    "password search."
                ),
                url=(
                    "https://github.com/"
                    "qa-team/qa-mcp/issues/1"
                ),
                repository="qa-team/qa-mcp",
                author="mock-user",
            ),
            GitHubIssue(
                number=2,
                title="Mock login validation issue",
                state="open",
                body=(
                    "Mock login validation "
                    "issue."
                ),
                url=(
                    "https://github.com/"
                    "qa-team/qa-mcp/issues/2"
                ),
                repository="qa-team/qa-mcp",
                author="mock-user",
            ),
        ]

        return issues[:max_results]