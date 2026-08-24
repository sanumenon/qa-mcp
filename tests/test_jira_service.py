import pytest

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
        key="QA-201",
        summary="Password reset fails",
        description=(
            "Password reset does not work "
            "for registered users."
        ),
        issue_type="Bug",
        status="Open",
        priority="High",
        project_key="QA",
        project_name="Customer Portal",
    )


def create_service():

    client = MockJiraClient(
        issues=[
            sample_issue()
        ]
    )

    return JiraService(
        client
    )


def test_service_get_issue():

    service = create_service()

    result = service.get_issue(
        "QA-201"
    )

    assert (
        result.key
        == "QA-201"
    )

    assert (
        result.summary
        == "Password reset fails"
    )


def test_service_trims_issue_key():

    service = create_service()

    result = service.get_issue(
        "  QA-201  "
    )

    assert (
        result.key
        == "QA-201"
    )


def test_service_rejects_empty_issue_key():

    service = create_service()

    with pytest.raises(
        ValueError,
        match="issue key cannot be empty",
    ):

        service.get_issue(
            "   "
        )


def test_service_search_issues():

    service = create_service()

    result = service.search_issues(
        "project = QA"
    )

    assert (
        result.total
        == 1
    )

    assert (
        result.issues[0].key
        == "QA-201"
    )


def test_service_trims_jql():

    service = create_service()

    result = service.search_issues(
        "  project = QA  "
    )

    assert (
        result.total
        == 1
    )


def test_service_rejects_empty_jql():

    service = create_service()

    with pytest.raises(
        ValueError,
        match="JQL cannot be empty",
    ):

        service.search_issues(
            "   "
        )


def test_service_rejects_invalid_max_results():

    service = create_service()

    with pytest.raises(
        ValueError,
        match="max_results must be greater than 0",
    ):

        service.search_issues(
            "project = QA",
            max_results=0,
        )