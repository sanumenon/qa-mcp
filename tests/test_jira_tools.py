import pytest

import qa_mcp.server as server

from qa_mcp.core.jira.service import (
    JiraService,
)

from qa_mcp.infrastructure.jira.mock_client import (
    MockJiraClient,
)

from qa_mcp.models.schemas import (
    JiraIssue,
)


def sample_issue():

    return JiraIssue(
        key="QA-501",
        summary="Password reset bug",
        description="Reset flow fails.",
        issue_type="Bug",
        status="Open",
        priority="High",
        project_key="QA",
        project_name="Customer Portal",
    )


def test_get_jira_issue_requires_configuration():

    with pytest.raises(
        ValueError,
        match="Jira connector is not configured",
    ):
        server.get_jira_issue(
            "QA-101"
        )


def test_search_jira_issues_requires_configuration():

    with pytest.raises(
        ValueError,
        match="Jira connector is not configured",
    ):
        server.search_jira_issues(
            "project = QA"
        )


def test_get_jira_issue_with_mock():

    original = server.jira_service

    try:

        server.jira_service = JiraService(
            MockJiraClient(
                issues=[
                    sample_issue()
                ]
            )
        )

        result = server.get_jira_issue(
            "QA-501"
        )

        assert (
            result["key"]
            == "QA-501"
        )

        assert (
            result["summary"]
            == "Password reset bug"
        )

    finally:

        server.jira_service = original


def test_search_jira_issues_with_mock():

    original = server.jira_service

    try:

        server.jira_service = JiraService(
            MockJiraClient(
                issues=[
                    sample_issue()
                ]
            )
        )

        result = server.search_jira_issues(
            "project = QA"
        )

        assert (
            result["total"]
            == 1
        )

        assert (
            result["issues"][0]["key"]
            == "QA-501"
        )

    finally:

        server.jira_service = original