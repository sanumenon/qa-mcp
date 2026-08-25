from typing import Any

import requests

from qa_mcp.infrastructure.github.client import (
    GitHubClient,
)

from qa_mcp.models.schemas import (
    GitHubIssue,
    GitHubPullRequest,
    GitHubRepository,
)


class GitHubCloudClient(GitHubClient):
    """GitHub REST API client."""

    def __init__(
        self,
        base_url: str,
        token: str,
    ):
        if not base_url.strip():
            raise ValueError(
                "GitHub base URL cannot be empty"
            )

        if not token.strip():
            raise ValueError(
                "GitHub token cannot be empty"
            )

        self.base_url = base_url.rstrip("/")
        self.token = token

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> requests.Response:

        url = (
            f"{self.base_url}"
            f"{path}"
        )

        headers = {
            "Accept": (
                "application/vnd.github+json"
            ),
            "Authorization": (
                f"Bearer {self.token}"
            ),
            "X-GitHub-Api-Version": (
                "2022-11-28"
            ),
        }

        response = requests.request(
            method,
            url,
            headers=headers,
            **kwargs,
        )

        response.raise_for_status()

        return response

    def get_repository(
        self,
        owner: str,
        repository: str,
    ) -> GitHubRepository:

        response = self._request(
            "GET",
            (
                f"/repos/"
                f"{owner}/{repository}"
            ),
        )

        data = response.json()

        return GitHubRepository(
            full_name=data["full_name"],
            name=data["name"],
            owner=data["owner"]["login"],
            description=(
                data.get("description")
                or ""
            ),
            url=data.get(
                "html_url",
                "",
            ),
            default_branch=data.get(
                "default_branch",
                "",
            ),
        )

    def get_issue(
        self,
        owner: str,
        repository: str,
        issue_number: int,
    ) -> GitHubIssue:

        response = self._request(
            "GET",
            (
                f"/repos/"
                f"{owner}/{repository}"
                f"/issues/{issue_number}"
            ),
        )

        data = response.json()

        return GitHubIssue(
            number=data["number"],
            title=data["title"],
            state=data.get(
                "state",
                "",
            ),
            body=(
                data.get("body")
                or ""
            ),
            url=data.get(
                "html_url",
                "",
            ),
            repository=(
                f"{owner}/{repository}"
            ),
            author=(
                data.get("user", {})
                .get("login", "")
            ),
        )

    def get_pull_request(
        self,
        owner: str,
        repository: str,
        pull_number: int,
    ) -> GitHubPullRequest:

        response = self._request(
            "GET",
            (
                f"/repos/"
                f"{owner}/{repository}"
                f"/pulls/{pull_number}"
            ),
        )

        data = response.json()

        return GitHubPullRequest(
            number=data["number"],
            title=data["title"],
            state=data.get(
                "state",
                "",
            ),
            body=(
                data.get("body")
                or ""
            ),
            url=data.get(
                "html_url",
                "",
            ),
            repository=(
                f"{owner}/{repository}"
            ),
            author=(
                data.get("user", {})
                .get("login", "")
            ),
            head_branch=(
                data.get("head", {})
                .get("ref", "")
            ),
            base_branch=(
                data.get("base", {})
                .get("ref", "")
            ),
        )

    def search_issues(
        self,
        query: str,
        max_results: int = 50,
    ) -> list[GitHubIssue]:

        response = self._request(
            "GET",
            "/search/issues",
            params={
                "q": query,
                "per_page": max_results,
            },
        )

        data = response.json()

        issues = []

        for item in data.get(
            "items",
            [],
        ):
            repository_url = (
                item.get(
                    "repository_url",
                    "",
                )
            )

            repository = (
                repository_url
                .replace(
                    "https://api.github.com/repos/",
                    "",
                )
            )

            issues.append(
                GitHubIssue(
                    number=item["number"],
                    title=item["title"],
                    state=item.get(
                        "state",
                        "",
                    ),
                    body=(
                        item.get("body")
                        or ""
                    ),
                    url=item.get(
                        "html_url",
                        "",
                    ),
                    repository=repository,
                    author=(
                        item.get(
                            "user",
                            {},
                        ).get(
                            "login",
                            "",
                        )
                    ),
                )
            )

        return issues