from qa_mcp.core.github.service import (
    GitHubService,
)
from qa_mcp.infrastructure.github.mock_client import (
    MockGitHubClient,
)


def create_service() -> GitHubService:
    return GitHubService(
        MockGitHubClient()
    )


def test_get_repository():

    service = create_service()

    result = service.get_repository(
        owner="qa-team",
        repository="qa-mcp",
    )

    assert result.full_name == "qa-team/qa-mcp"
    assert result.name == "qa-mcp"


def test_get_issue():

    service = create_service()

    result = service.get_issue(
        owner="qa-team",
        repository="qa-mcp",
        issue_number=1,
    )

    assert result.number == 1
    assert result.repository == "qa-team/qa-mcp"


def test_get_pull_request():

    service = create_service()

    result = service.get_pull_request(
        owner="qa-team",
        repository="qa-mcp",
        pull_number=1,
    )

    assert result.number == 1
    assert result.repository == "qa-team/qa-mcp"


def test_search_issues():

    service = create_service()

    result = service.search_issues(
        query="password",
    )

    assert isinstance(result, list)
    assert len(result) > 0


def test_service_rejects_empty_owner():

    service = create_service()

    try:
        service.get_repository(
            owner="",
            repository="qa-mcp",
        )
        assert False
    except ValueError as exc:
        assert "owner" in str(exc).lower()


def test_service_rejects_empty_repository():

    service = create_service()

    try:
        service.get_repository(
            owner="qa-team",
            repository="",
        )
        assert False
    except ValueError as exc:
        assert "repository" in str(exc).lower()


def test_service_rejects_invalid_issue_number():

    service = create_service()

    try:
        service.get_issue(
            owner="qa-team",
            repository="qa-mcp",
            issue_number=0,
        )
        assert False
    except ValueError as exc:
        assert "issue" in str(exc).lower()


def test_service_rejects_invalid_pull_request_number():

    service = create_service()

    try:
        service.get_pull_request(
            owner="qa-team",
            repository="qa-mcp",
            pull_number=0,
        )
        assert False
    except ValueError as exc:
        assert "pull" in str(exc).lower()