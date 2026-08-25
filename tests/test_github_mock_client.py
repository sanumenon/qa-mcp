from qa_mcp.infrastructure.github.mock_client import (
    MockGitHubClient,
)


def test_mock_github_client_get_repository():

    client = MockGitHubClient()

    result = client.get_repository(
        owner="qa-team",
        repository="qa-mcp",
    )

    assert result.full_name == "qa-team/qa-mcp"
    assert result.name == "qa-mcp"
    assert result.owner == "qa-team"


def test_mock_github_client_get_issue():

    client = MockGitHubClient()

    result = client.get_issue(
        owner="qa-team",
        repository="qa-mcp",
        issue_number=1,
    )

    assert result.number == 1
    assert result.repository == "qa-team/qa-mcp"
    assert result.title


def test_mock_github_client_get_pull_request():

    client = MockGitHubClient()

    result = client.get_pull_request(
        owner="qa-team",
        repository="qa-mcp",
        pull_number=1,
    )

    assert result.number == 1
    assert result.repository == "qa-team/qa-mcp"
    assert result.title


def test_mock_github_client_search_issues():

    client = MockGitHubClient()

    result = client.search_issues(
        query="password",
    )

    assert isinstance(result, list)
    assert len(result) > 0

    for issue in result:
        assert issue.number > 0
        assert issue.title