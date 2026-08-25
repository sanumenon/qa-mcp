from unittest.mock import Mock, patch

import pytest

from qa_mcp.infrastructure.slack.cloud_client import (
    SlackCloudClient,
)
from qa_mcp.models.schemas import (
    SlackChannel,
    SlackMessage,
    SlackSearchResult,
    SlackThread,
)


def test_slack_cloud_client_rejects_empty_url():

    with pytest.raises(
        ValueError,
        match="Slack base URL cannot be empty",
    ):
        SlackCloudClient(
            base_url="",
            token="test-token",
        )


def test_slack_cloud_client_rejects_empty_token():

    with pytest.raises(
        ValueError,
        match="Slack token cannot be empty",
    ):
        SlackCloudClient(
            base_url="https://slack.com/api",
            token="",
        )


@patch(
    "qa_mcp.infrastructure.slack.cloud_client.requests.request"
)
def test_get_channel(
    mock_request,
):

    response = Mock()

    response.json.return_value = {
        "ok": True,
        "channel": {
            "id": "C123",
            "name": "qa-channel",
            "is_private": False,
            "is_archived": False,
        },
    }

    mock_request.return_value = response

    client = SlackCloudClient(
        base_url="https://slack.com/api",
        token="test-token",
    )

    result = client.get_channel(
        "qa-channel"
    )

    assert isinstance(
        result,
        SlackChannel,
    )

    assert result.id == "C123"
    assert result.name == "qa-channel"

    mock_request.assert_called_once()


@patch(
    "qa_mcp.infrastructure.slack.cloud_client.requests.request"
)
def test_get_messages(
    mock_request,
):

    response = Mock()

    response.json.return_value = {
        "ok": True,
        "messages": [
            {
                "ts": "1700000000.000001",
                "text": "Password reset issue",
                "user": "U123",
            }
        ],
    }

    mock_request.return_value = response

    client = SlackCloudClient(
        base_url="https://slack.com/api",
        token="test-token",
    )

    result = client.get_messages(
        "C123",
        limit=10,
    )

    assert len(result) == 1
    assert isinstance(
        result[0],
        SlackMessage,
    )

    assert result[0].text == (
        "Password reset issue"
    )


@patch(
    "qa_mcp.infrastructure.slack.cloud_client.requests.request"
)
def test_search_messages(
    mock_request,
):

    response = Mock()

    response.json.return_value = {
        "ok": True,
        "messages": {
            "matches": [
                {
                    "ts": "1700000000.000001",
                    "text": "Password reset issue",
                    "username": "tester",
                    "channel": {
                        "name": "qa-channel",
                    },
                    "permalink": (
                        "https://slack.com/archives/"
                        "C123/p1700000000000001"
                    ),
                }
            ],
            "total": 1,
        },
    }

    mock_request.return_value = response

    client = SlackCloudClient(
        base_url="https://slack.com/api",
        token="test-token",
    )

    result = client.search_messages(
        "password",
        max_results=10,
    )

    assert isinstance(
        result,
        SlackSearchResult,
    )

    assert result.total == 1
    assert len(result.messages) == 1
    assert (
        result.messages[0].text
        == "Password reset issue"
    )


@patch(
    "qa_mcp.infrastructure.slack.cloud_client.requests.request"
)
def test_get_thread(
    mock_request,
):

    response = Mock()

    response.json.return_value = {
        "ok": True,
        "messages": [
            {
                "ts": "1700000000.000001",
                "text": "Root message",
                "user": "U123",
            },
            {
                "ts": "1700000000.000002",
                "text": "Reply",
                "user": "U456",
                "thread_ts": (
                    "1700000000.000001"
                ),
            },
        ],
    }

    mock_request.return_value = response

    client = SlackCloudClient(
        base_url="https://slack.com/api",
        token="test-token",
    )

    result = client.get_thread(
        "C123",
        "1700000000.000001",
    )

    assert isinstance(
        result,
        SlackThread,
    )

    assert result.channel == "C123"
    assert result.thread_ts == (
        "1700000000.000001"
    )

    assert len(result.messages) == 2


@patch(
    "qa_mcp.infrastructure.slack.cloud_client.requests.request"
)
def test_slack_api_error(
    mock_request,
):

    response = Mock()

    response.json.return_value = {
        "ok": False,
        "error": "invalid_auth",
    }

    mock_request.return_value = response

    client = SlackCloudClient(
        base_url="https://slack.com/api",
        token="test-token",
    )

    with pytest.raises(
        ValueError,
        match="Slack authentication failed",
    ):
        client.get_channel(
            "qa-channel"
        )