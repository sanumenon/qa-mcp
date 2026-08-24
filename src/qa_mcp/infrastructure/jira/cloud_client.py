from __future__ import annotations

import base64
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from qa_mcp.infrastructure.jira.client import JiraClient
from qa_mcp.models.schemas import (
    JiraIssue,
    JiraSearchResult,
)


class JiraCloudClient(JiraClient):
    """Read-only Jira Cloud REST API client."""

    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
        opener=urlopen,
    ):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_token = api_token
        self.opener = opener

        if not self.base_url:
            raise ValueError(
                "Jira URL cannot be empty"
            )

        if not self.email:
            raise ValueError(
                "Jira email cannot be empty"
            )

        if not self.api_token:
            raise ValueError(
                "Jira API token cannot be empty"
            )

    def _auth_header(self) -> str:
        credentials = (
            f"{self.email}:{self.api_token}"
        )

        encoded = base64.b64encode(
            credentials.encode("utf-8")
        ).decode("ascii")

        return f"Basic {encoded}"

    def _get_json(
        self,
        path: str,
        params: dict[str, str | int] | None = None,
    ) -> dict:

        url = (
            f"{self.base_url}"
            f"{path}"
        )

        if params:
            url = (
                f"{url}?{urlencode(params)}"
            )

        request = Request(
            url,
            method="GET",
            headers={
                "Accept": "application/json",
                "Authorization": (
                    self._auth_header()
                ),
            },
        )

        try:
            with self.opener(request) as response:
                return json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

        except HTTPError as exc:
            if exc.code == 401:
                raise ValueError(
                    "Jira authentication failed"
                ) from exc

            if exc.code == 403:
                raise ValueError(
                    "Jira access forbidden"
                ) from exc

            if exc.code == 404:
                raise ValueError(
                    "Jira resource not found"
                ) from exc

            raise ValueError(
                f"Jira API request failed: "
                f"HTTP {exc.code}"
            ) from exc

        except URLError as exc:
            raise ValueError(
                "Unable to connect to Jira"
            ) from exc

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Jira returned invalid JSON"
            ) from exc

    @staticmethod
    def _user_name(
        user: dict | None,
    ) -> str:

        if not user:
            return ""

        return (
            user.get("displayName")
            or user.get("emailAddress")
            or user.get("accountId")
            or ""
        )

    @staticmethod
    def _description(
        description,
    ) -> str:

        if isinstance(
            description,
            str,
        ):
            return description

        if not description:
            return ""

        return json.dumps(
            description,
            ensure_ascii=False,
        )

    def _normalize_issue(
        self,
        data: dict,
    ) -> JiraIssue:

        fields = data.get(
            "fields",
            {},
        )

        project = fields.get(
            "project"
        ) or {}

        issue_type = fields.get(
            "issuetype"
        ) or {}

        status = fields.get(
            "status"
        ) or {}

        priority = fields.get(
            "priority"
        ) or {}

        return JiraIssue(
            key=data.get(
                "key",
                "",
            ),
            summary=fields.get(
                "summary",
                "",
            ),
            description=self._description(
                fields.get(
                    "description"
                )
            ),
            issue_type=issue_type.get(
                "name",
                "",
            ),
            status=status.get(
                "name",
                "",
            ),
            priority=priority.get(
                "name",
                "",
            ),
            project_key=project.get(
                "key",
                "",
            ),
            project_name=project.get(
                "name",
                "",
            ),
            assignee=self._user_name(
                fields.get(
                    "assignee"
                )
            ),
            reporter=self._user_name(
                fields.get(
                    "reporter"
                )
            ),
            url=(
                f"{self.base_url}"
                f"/browse/"
                f"{data.get('key', '')}"
            ),
        )

    def get_issue(
        self,
        issue_key: str,
    ) -> JiraIssue:

        if not issue_key.strip():
            raise ValueError(
                "Jira issue key cannot be empty"
            )

        data = self._get_json(
            f"/rest/api/3/issue/"
            f"{issue_key.strip()}",
            params={
                "fields": (
                    "summary,description,"
                    "issuetype,status,priority,"
                    "project,assignee,reporter"
                )
            },
        )

        return self._normalize_issue(
            data
        )

    def search_issues(
        self,
        jql: str,
        max_results: int = 50,
    ) -> JiraSearchResult:

        if not jql.strip():
            raise ValueError(
                "Jira JQL cannot be empty"
            )

        if max_results < 1:
            raise ValueError(
                "max_results must be greater than 0"
            )

        data = self._get_json(
            "/rest/api/3/search/jql",
            params={
                "jql": jql.strip(),
                "maxResults": max_results,
                "fields": (
                    "summary,description,"
                    "issuetype,status,priority,"
                    "project,assignee,reporter"
                ),
            },
        )

        issues = [
            self._normalize_issue(
                issue
            )
            for issue in data.get(
                "issues",
                [],
            )
        ]

        return JiraSearchResult(
            issues=issues,
            total=len(issues),
        )