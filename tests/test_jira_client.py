import pytest

from qa_mcp.infrastructure.jira.mock_client import (
    MockJiraClient,
)

from qa_mcp.models.schemas import (
    JiraIssue,
)


def sample_issue():

    return JiraIssue(
        key="QA-101",
        summary="User cannot reset password",
        description=(
            "Registered users cannot reset "
            "their password."
        ),
        issue_type="Bug",
        status="Open",
        priority="High",
        project_key="QA",
        project_name="Customer Portal",
        assignee="QA Engineer",
        reporter="Product Owner",
        url=(
            "https://example.atlassian.net/"
            "browse/QA-101"
        ),
    )


def test_mock_jira_get_issue():

    client = MockJiraClient(
        issues=[
            sample_issue()
        ]
    )

    result = client.get_issue(
        "QA-101"
    )

    assert (
        result.key
        == "QA-101"
    )

    assert (
        result.summary
        == "User cannot reset password"
    )

    assert (
        result.issue_type
        == "Bug"
    )


def test_mock_jira_rejects_missing_issue():

    client = MockJiraClient()

    with pytest.raises(
        ValueError,
        match="Jira issue not found",
    ):

        client.get_issue(
            "QA-999"
        )


def test_mock_jira_search():

    client = MockJiraClient(
        issues=[
            sample_issue()
        ]
    )

    result = client.search_issues(
        "project = QA"
    )

    assert (
        result.total
        == 1
    )

    assert (
        len(result.issues)
        == 1
    )

    assert (
        result.issues[0].key
        == "QA-101"
    )


def test_mock_jira_search_respects_max_results():

    issues = [

        JiraIssue(
            key=f"QA-{index}",
            summary=f"Issue {index}",
        )

        for index in range(
            1,
            6,
        )
    ]

    client = MockJiraClient(
        issues=issues
    )

    result = client.search_issues(
        "project = QA",
        max_results=2,
    )

    assert (
        result.total
        == 2
    )

    assert (
        len(result.issues)
        == 2
    )