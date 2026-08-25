from unittest.mock import Mock

from qa_mcp.models.schemas import (
    GitHubIssue,
    GitHubPullRequest,
    GitHubRepository,
)

import pytest

def test_get_github_repository_tool(monkeypatch):

    from qa_mcp import server

    mock_service = Mock()

    mock_service.get_repository.return_value = (
        GitHubRepository(
            full_name="qa-team/qa-mcp",
            name="qa-mcp",
            owner="qa-team",
            description="QA MCP",
            url=(
                "https://github.com/"
                "qa-team/qa-mcp"
            ),
            default_branch="main",
        )
    )

    monkeypatch.setattr(
        server,
        "github_service",
        mock_service,
    )

    result = server.get_github_repository(
        owner="qa-team",
        repository="qa-mcp",
    )

    assert (
        result["full_name"]
        == "qa-team/qa-mcp"
    )

    assert (
        result["default_branch"]
        == "main"
    )

    mock_service.get_repository.assert_called_once_with(
        owner="qa-team",
        repository="qa-mcp",
    )


def test_get_github_issue_tool(monkeypatch):

    from qa_mcp import server

    mock_service = Mock()

    mock_service.get_issue.return_value = (
        GitHubIssue(
            number=12,
            title="Password reset fails",
            state="open",
            body="Reset failure",
            url=(
                "https://github.com/"
                "qa-team/qa-mcp/issues/12"
            ),
            repository="qa-team/qa-mcp",
            author="tester",
        )
    )

    monkeypatch.setattr(
        server,
        "github_service",
        mock_service,
    )

    result = server.get_github_issue(
        owner="qa-team",
        repository="qa-mcp",
        issue_number=12,
    )

    assert result["number"] == 12
    assert (
        result["title"]
        == "Password reset fails"
    )

    mock_service.get_issue.assert_called_once_with(
        owner="qa-team",
        repository="qa-mcp",
        issue_number=12,
    )


def test_get_github_pull_request_tool(
    monkeypatch,
):

    from qa_mcp import server

    mock_service = Mock()

    mock_service.get_pull_request.return_value = (
        GitHubPullRequest(
            number=7,
            title="Add password validation",
            state="open",
            body="Adds validation",
            url=(
                "https://github.com/"
                "qa-team/qa-mcp/pull/7"
            ),
            repository="qa-team/qa-mcp",
            author="developer",
            head_branch="feature/password",
            base_branch="main",
        )
    )

    monkeypatch.setattr(
        server,
        "github_service",
        mock_service,
    )

    result = server.get_github_pull_request(
        owner="qa-team",
        repository="qa-mcp",
        pull_number=7,
    )

    assert result["number"] == 7

    assert (
        result["head_branch"]
        == "feature/password"
    )

    assert (
        result["base_branch"]
        == "main"
    )

    mock_service.get_pull_request.assert_called_once_with(
        owner="qa-team",
        repository="qa-mcp",
        pull_number=7,
    )


def test_search_github_issues_tool(
    monkeypatch,
):

    from qa_mcp import server

    mock_service = Mock()

    mock_service.search_issues.return_value = [
        GitHubIssue(
            number=1,
            title="Password reset issue",
            state="open",
            body="Password reset fails",
            url=(
                "https://github.com/"
                "qa-team/qa-mcp/issues/1"
            ),
            repository="qa-team/qa-mcp",
            author="tester",
        ),
        GitHubIssue(
            number=2,
            title="Login validation issue",
            state="open",
            body="Login validation fails",
            url=(
                "https://github.com/"
                "qa-team/qa-mcp/issues/2"
            ),
            repository="qa-team/qa-mcp",
            author="developer",
        ),
    ]

    monkeypatch.setattr(
        server,
        "github_service",
        mock_service,
    )

    result = server.search_github_issues(
        query="password",
        max_results=10,
    )

    assert len(result) == 2
    assert result[0]["number"] == 1
    assert result[1]["number"] == 2

    mock_service.search_issues.assert_called_once_with(
        query="password",
        max_results=10,
    )

def test_github_tools_reject_when_connector_disabled(
    monkeypatch,
):
    from qa_mcp import server

    monkeypatch.setattr(
        server,
        "github_service",
        None,
    )

    with pytest.raises(
        RuntimeError,
        match="GitHub connector is not configured",
    ):
        server.get_github_repository(
            owner="qa-team",
            repository="qa-mcp",
        )