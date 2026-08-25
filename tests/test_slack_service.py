from unittest.mock import Mock

import pytest

from qa_mcp.infrastructure.slack.client import SlackClient
from qa_mcp.models.schemas import (
    SlackChannel,
    SlackMessage,
    SlackSearchResult,
    SlackThread,
)

from qa_mcp.core.slack.service import (
    SlackService,
)

def test_slack_service_requires_client():

    client = Mock(spec=SlackClient)

    service = SlackService(client)

    assert service is not None


def test_get_channel_delegates_to_client():

    client = Mock(spec=SlackClient)

    expected = SlackChannel(
        id="C123",
        name="qa-channel",
    )

    client.get_channel.return_value = expected

    service = SlackService(client)

    result = service.get_channel(
        "qa-channel"
    )

    client.get_channel.assert_called_once_with(
        "qa-channel"
    )

    assert result == expected


def test_get_messages_delegates_to_client():

    client = Mock(spec=SlackClient)

    expected = [
        SlackMessage(
            ts="1700000000.000001",
            text="Test message",
            user="tester",
            channel="qa-channel",
        )
    ]

    client.get_messages.return_value = expected

    service = SlackService(client)

    result = service.get_messages(
        "qa-channel",
        limit=10,
    )

    client.get_messages.assert_called_once_with(
        "qa-channel",
        limit=10,
    )

    assert result == expected


def test_search_messages_delegates_to_client():

    client = Mock(spec=SlackClient)

    expected = SlackSearchResult(
        messages=[
            SlackMessage(
                ts="1700000000.000001",
                text="Password issue",
                user="tester",
                channel="qa-channel",
            )
        ],
        total=1,
    )

    client.search_messages.return_value = expected

    service = SlackService(client)

    result = service.search_messages(
        "password",
        max_results=10,
    )

    client.search_messages.assert_called_once_with(
        "password",
        max_results=10,
    )

    assert result == expected


def test_get_thread_delegates_to_client():

    client = Mock(spec=SlackClient)

    expected = SlackThread(
        channel="qa-channel",
        thread_ts="1700000000.000001",
        messages=[],
    )

    client.get_thread.return_value = expected

    service = SlackService(client)

    result = service.get_thread(
        "qa-channel",
        "1700000000.000001",
    )

    client.get_thread.assert_called_once_with(
        "qa-channel",
        "1700000000.000001",
    )

    assert result == expected


def test_slack_service_propagates_client_error():

    client = Mock(spec=SlackClient)

    client.get_channel.side_effect = RuntimeError(
        "Slack unavailable"
    )

    service = SlackService(client)

    with pytest.raises(
        RuntimeError,
        match="Slack unavailable",
    ):
        service.get_channel(
            "qa-channel"
        )