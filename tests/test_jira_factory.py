from qa_mcp.core.jira.factory import (
    create_jira_service,
)


def test_jira_factory_disabled():

    config = {
        "features": {
            "jira_connector": False,
        },
        "jira": {
            "url": (
                "https://example.atlassian.net"
            ),
            "email": "qa@example.com",
            "api_token": "secret-token",
        },
    }

    result = create_jira_service(
        config
    )

    assert result is None


def test_jira_factory_missing_credentials():

    config = {
        "features": {
            "jira_connector": True,
        },
        "jira": {
            "url": "",
            "email": "",
            "api_token": "",
        },
    }

    result = create_jira_service(
        config
    )

    assert result is None


def test_jira_factory_creates_service():

    config = {
        "features": {
            "jira_connector": True,
        },
        "jira": {
            "url": (
                "https://example.atlassian.net"
            ),
            "email": "qa@example.com",
            "api_token": "secret-token",
        },
    }

    result = create_jira_service(
        config
    )

    assert result is not None

def test_jira_factory_rejects_whitespace_credentials():

    config = {
        "features": {
            "jira_connector": True,
        },
        "jira": {
            "url": "   ",
            "email": "qa@example.com",
            "api_token": "secret-token",
        },
    }

    result = create_jira_service(
        config
    )

    assert result is None


def test_jira_factory_creates_cloud_service():

    config = {
        "features": {
            "jira_connector": True,
        },
        "jira": {
            "url": (
                "https://example.atlassian.net"
            ),
            "email": "qa@example.com",
            "api_token": "secret-token",
        },
    }

    service = create_jira_service(
        config
    )

    assert service is not None

    assert (
        service.client.__class__.__name__
        == "JiraCloudClient"
    )