from qa_mcp.infrastructure.slack.mock_client import (
    MockSlackClient,
)
from qa_mcp.models.schemas import (
    SlackChannel,
    SlackMessage,
    SlackSearchResult,
    SlackThread,
)


def test_mock_slack_client_get_channel():

    client = MockSlackClient()

    result = client.get_channel(
        "qa-channel"
    )

    assert isinstance(
        result,
        SlackChannel,
    )

    assert result.name == "qa-channel"


def test_mock_slack_client_get_messages():

    client = MockSlackClient()

    result = client.get_messages(
        "qa-channel"
    )

    assert isinstance(
        result,
        list,
    )

    assert all(
        isinstance(
            item,
            SlackMessage,
        )
        for item in result
    )


def test_mock_slack_client_search_messages():

    client = MockSlackClient()

    result = client.search_messages(
        "password"
    )

    assert isinstance(
        result,
        SlackSearchResult,
    )

    assert all(
        isinstance(
            item,
            SlackMessage,
        )
        for item in result.messages
    )


def test_mock_slack_client_get_thread():

    client = MockSlackClient()

    result = client.get_thread(
        "qa-channel",
        "1700000000.000001",
    )

    assert isinstance(
        result,
        SlackThread,
    )

    assert (
        result.channel
        == "qa-channel"
    )

    assert (
        result.thread_ts
        == "1700000000.000001"
    )