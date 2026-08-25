from qa_mcp.core.slack.factory import (
    create_slack_service,
)
from qa_mcp.core.slack.service import (
    SlackService,
)
from qa_mcp.infrastructure.slack.cloud_client import (
    SlackCloudClient,
)


def test_slack_factory_disabled():

    config = {
        "features": {
            "slack_connector": False,
        },
        "slack": {
            "url": "https://slack.com/api",
            "token": "secret-token",
            "default_channel": "qa-channel",
        },
    }

    result = create_slack_service(
        config
    )

    assert result is None


def test_slack_factory_missing_token():

    config = {
        "features": {
            "slack_connector": True,
        },
        "slack": {
            "url": "https://slack.com/api",
            "token": "",
            "default_channel": "qa-channel",
        },
    }

    result = create_slack_service(
        config
    )

    assert result is None


def test_slack_factory_missing_url():

    config = {
        "features": {
            "slack_connector": True,
        },
        "slack": {
            "url": "",
            "token": "secret-token",
            "default_channel": "qa-channel",
        },
    }

    result = create_slack_service(
        config
    )

    assert result is None


def test_slack_factory_rejects_whitespace_credentials():

    config = {
        "features": {
            "slack_connector": True,
        },
        "slack": {
            "url": "   ",
            "token": "secret-token",
            "default_channel": "qa-channel",
        },
    }

    result = create_slack_service(
        config
    )

    assert result is None


def test_slack_factory_creates_service():

    config = {
        "features": {
            "slack_connector": True,
        },
        "slack": {
            "url": "https://slack.com/api",
            "token": "secret-token",
            "default_channel": "qa-channel",
        },
    }

    result = create_slack_service(
        config
    )

    assert isinstance(
        result,
        SlackService,
    )


def test_slack_factory_creates_cloud_client():

    config = {
        "features": {
            "slack_connector": True,
        },
        "slack": {
            "url": "https://slack.com/api",
            "token": "secret-token",
            "default_channel": "qa-channel",
        },
    }

    result = create_slack_service(
        config
    )

    assert isinstance(
        result.client,
        SlackCloudClient,
    )