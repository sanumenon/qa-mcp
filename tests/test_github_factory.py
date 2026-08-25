from qa_mcp.core.github.factory import (
    create_github_service,
)
from qa_mcp.core.github.service import (
    GitHubService,
)


def test_github_factory_disabled():

    config = {
        "features": {
            "github_connector": False,
        },
        "github": {
            "url": "https://api.github.com",
            "token": "secret-token",
            "owner": "qa-team",
        },
    }

    result = create_github_service(
        config
    )

    assert result is None


def test_github_factory_missing_credentials():

    config = {
        "features": {
            "github_connector": True,
        },
        "github": {
            "url": "",
            "token": "",
            "owner": "",
        },
    }

    result = create_github_service(
        config
    )

    assert result is None


def test_github_factory_creates_service():

    config = {
        "features": {
            "github_connector": True,
        },
        "github": {
            "url": (
                "https://api.github.com"
            ),
            "token": "secret-token",
            "owner": "qa-team",
        },
    }

    result = create_github_service(
        config
    )

    assert isinstance(
        result,
        GitHubService,
    )


def test_github_factory_rejects_whitespace_credentials():

    config = {
        "features": {
            "github_connector": True,
        },
        "github": {
            "url": "   ",
            "token": "secret-token",
            "owner": "qa-team",
        },
    }

    result = create_github_service(
        config
    )

    assert result is None


def test_github_factory_rejects_whitespace_token():

    config = {
        "features": {
            "github_connector": True,
        },
        "github": {
            "url": "https://api.github.com",
            "token": "   ",
            "owner": "qa-team",
        },
    }

    result = create_github_service(
        config
    )

    assert result is None


def test_github_factory_rejects_whitespace_owner():

    config = {
        "features": {
            "github_connector": True,
        },
        "github": {
            "url": "https://api.github.com",
            "token": "secret-token",
            "owner": "   ",
        },
    }

    result = create_github_service(
        config
    )

    assert result is None