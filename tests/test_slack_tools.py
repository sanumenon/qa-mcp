from unittest.mock import Mock

from qa_mcp.models.schemas import (
    SlackChannel,
    SlackMessage,
    SlackSearchResult,
    SlackThread,
)


def test_get_slack_channel_tool(monkeypatch):

    from qa_mcp import server

    mock_service = Mock()

    mock_service.get_channel.return_value = (
        SlackChannel(
            id="C123",
            name="qa-channel",
            is_private=False,
            is_archived=False,
            url=(
                "https://slack.com/archives/C123"
            ),
        )
    )

    monkeypatch.setattr(
        server,
        "slack_service",
        mock_service,
    )

    result = server.get_slack_channel(
        channel="qa-channel",
    )

    mock_service.get_channel.assert_called_once_with(
        "qa-channel"
    )

    assert result["id"] == "C123"
    assert result["name"] == "qa-channel"


def test_get_slack_messages_tool(monkeypatch):

    from qa_mcp import server

    mock_service = Mock()

    mock_service.get_messages.return_value = [
        SlackMessage(
            ts="1700000000.000001",
            text="Password reset issue",
            user="tester",
            channel="qa-channel",
        )
    ]

    monkeypatch.setattr(
        server,
        "slack_service",
        mock_service,
    )

    result = server.get_slack_messages(
        channel="qa-channel",
        limit=10,
    )

    mock_service.get_messages.assert_called_once_with(
        "qa-channel",
        limit=10,
    )

    assert len(result) == 1
    assert result[0]["text"] == (
        "Password reset issue"
    )


def test_search_slack_messages_tool(monkeypatch):

    from qa_mcp import server

    mock_service = Mock()

    mock_service.search_messages.return_value = (
        SlackSearchResult(
            messages=[
                SlackMessage(
                    ts="1700000000.000001",
                    text="Password reset issue",
                    user="tester",
                    channel="qa-channel",
                )
            ],
            total=1,
        )
    )

    monkeypatch.setattr(
        server,
        "slack_service",
        mock_service,
    )

    result = server.search_slack_messages(
        query="password",
        max_results=10,
    )

    mock_service.search_messages.assert_called_once_with(
        "password",
        max_results=10,
    )

    assert result["total"] == 1
    assert len(result["messages"]) == 1


def test_get_slack_thread_tool(monkeypatch):

    from qa_mcp import server

    mock_service = Mock()

    mock_service.get_thread.return_value = (
        SlackThread(
            channel="qa-channel",
            thread_ts="1700000000.000001",
            messages=[
                SlackMessage(
                    ts="1700000000.000001",
                    text="Root message",
                    user="tester",
                    channel="qa-channel",
                    thread_ts="1700000000.000001",
                )
            ],
        )
    )

    monkeypatch.setattr(
        server,
        "slack_service",
        mock_service,
    )

    result = server.get_slack_thread(
        channel="qa-channel",
        thread_ts="1700000000.000001",
    )

    mock_service.get_thread.assert_called_once_with(
        "qa-channel",
        "1700000000.000001",
    )

    assert result["channel"] == "qa-channel"
    assert result["thread_ts"] == (
        "1700000000.000001"
    )
    assert len(result["messages"]) == 1