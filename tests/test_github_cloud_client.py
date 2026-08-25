from unittest.mock import Mock

import pytest

from qa_mcp.infrastructure.github.cloud_client import (
    GitHubCloudClient,
)


def create_client():

    return GitHubCloudClient(
        base_url="https://api.github.com",
        token="secret-token",
    )


def test_get_repository():

    response = Mock()

    response.json.return_value = {
        "full_name": "qa-team/qa-mcp",
        "name": "qa-mcp",
        "owner": {
            "login": "qa-team",
        },
        "description": "QA MCP project",
        "html_url": (
            "https://github.com/qa-team/qa-mcp"
        ),
        "default_branch": "main",
    }

    response.raise_for_status.return_value = None

    client = create_client()

    client._request = Mock(
        return_value=response
    )

    result = client.get_repository(
        owner="qa-team",
        repository="qa-mcp",
    )

    assert result.full_name == "qa-team/qa-mcp"
    assert result.name == "qa-mcp"
    assert result.owner == "qa-team"
    assert result.default_branch == "main"

    client._request.assert_called_once_with(
        "GET",
        "/repos/qa-team/qa-mcp",
    )


def test_get_issue():

    response = Mock()

    response.json.return_value = {
        "number": 12,
        "title": "Password reset fails",
        "state": "open",
        "body": "Reset password validation fails.",
        "html_url": (
            "https://github.com/"
            "qa-team/qa-mcp/issues/12"
        ),
        "repository_url": (
            "https://api.github.com/repos/"
            "qa-team/qa-mcp"
        ),
        "user": {
            "login": "tester",
        },
    }

    response.raise_for_status.return_value = None

    client = create_client()

    client._request = Mock(
        return_value=response
    )

    result = client.get_issue(
        owner="qa-team",
        repository="qa-mcp",
        issue_number=12,
    )

    assert result.number == 12
    assert result.title == "Password reset fails"
    assert result.repository == "qa-team/qa-mcp"
    assert result.author == "tester"

    client._request.assert_called_once_with(
        "GET",
        "/repos/qa-team/qa-mcp/issues/12",
    )


def test_get_pull_request():

    response = Mock()

    response.json.return_value = {
        "number": 7,
        "title": "Add password validation",
        "state": "open",
        "body": "Adds validation.",
        "html_url": (
            "https://github.com/"
            "qa-team/qa-mcp/pull/7"
        ),
        "user": {
            "login": "developer",
        },
        "head": {
            "ref": "feature/password",
        },
        "base": {
            "ref": "main",
        },
    }

    response.raise_for_status.return_value = None

    client = create_client()

    client._request = Mock(
        return_value=response
    )

    result = client.get_pull_request(
        owner="qa-team",
        repository="qa-mcp",
        pull_number=7,
    )

    assert result.number == 7
    assert result.title == (
        "Add password validation"
    )
    assert result.author == "developer"
    assert result.head_branch == (
        "feature/password"
    )
    assert result.base_branch == "main"

    client._request.assert_called_once_with(
        "GET",
        "/repos/qa-team/qa-mcp/pulls/7",
    )


def test_search_issues():

    response = Mock()

    response.json.return_value = {
        "total_count": 2,
        "items": [
            {
                "number": 1,
                "title": "Password reset issue",
                "state": "open",
                "body": "Password reset fails.",
                "html_url": (
                    "https://github.com/"
                    "qa-team/qa-mcp/issues/1"
                ),
                "repository_url": (
                    "https://api.github.com/repos/"
                    "qa-team/qa-mcp"
                ),
                "user": {
                    "login": "tester",
                },
            },
            {
                "number": 2,
                "title": "Login issue",
                "state": "open",
                "body": "Login validation fails.",
                "html_url": (
                    "https://github.com/"
                    "qa-team/qa-mcp/issues/2"
                ),
                "repository_url": (
                    "https://api.github.com/repos/"
                    "qa-team/qa-mcp"
                ),
                "user": {
                    "login": "developer",
                },
            },
        ],
    }

    response.raise_for_status.return_value = None

    client = create_client()

    client._request = Mock(
        return_value=response
    )

    result = client.search_issues(
        query="password",
        max_results=10,
    )

    assert len(result) == 2
    assert result[0].number == 1
    assert result[1].number == 2

    client._request.assert_called_once_with(
        "GET",
        "/search/issues",
        params={
            "q": "password",
            "per_page": 10,
        },
    )


def test_cloud_client_rejects_empty_token():

    with pytest.raises(ValueError):

        GitHubCloudClient(
            base_url="https://api.github.com",
            token="",
        )


def test_cloud_client_rejects_empty_base_url():

    with pytest.raises(ValueError):

        GitHubCloudClient(
            base_url="",
            token="secret-token",
        )