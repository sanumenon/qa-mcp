from qa_mcp.infrastructure.slack.client import (
    SlackClient,
)
from qa_mcp.models.schemas import (
    SlackChannel,
    SlackMessage,
    SlackSearchResult,
    SlackThread,
)


class MockSlackClient(SlackClient):
    """In-memory Slack client for local development and tests."""

    def get_channel(
        self,
        channel: str,
    ) -> SlackChannel:

        return SlackChannel(
            id="C00000001",
            name=channel,
            is_private=False,
            is_archived=False,
            url=(
                "https://slack.com/"
                f"archives/{channel}"
            ),
        )

    def get_messages(
        self,
        channel: str,
        limit: int = 50,
    ) -> list[SlackMessage]:

        messages = [
            SlackMessage(
                ts="1700000000.000001",
                text="Password reset issue reported.",
                user="tester",
                channel=channel,
                url=(
                    "https://slack.com/"
                    f"archives/{channel}/"
                    "p1700000000000001"
                ),
            ),
            SlackMessage(
                ts="1700000000.000002",
                text="Investigating the issue.",
                user="developer",
                channel=channel,
                url=(
                    "https://slack.com/"
                    f"archives/{channel}/"
                    "p1700000000000002"
                ),
            ),
        ]

        return messages[:limit]

    def search_messages(
        self,
        query: str,
        max_results: int = 50,
    ) -> SlackSearchResult:

        messages = [
            SlackMessage(
                ts="1700000000.000001",
                text=(
                    f"Mock result for: {query}"
                ),
                user="tester",
                channel="qa-channel",
            )
        ]

        messages = messages[:max_results]

        return SlackSearchResult(
            messages=messages,
            total=len(messages),
        )

    def get_thread(
        self,
        channel: str,
        thread_ts: str,
    ) -> SlackThread:

        messages = [
            SlackMessage(
                ts=thread_ts,
                text="Root message",
                user="tester",
                channel=channel,
                thread_ts=thread_ts,
            ),
            SlackMessage(
                ts="1700000000.000002",
                text="Mock thread reply.",
                user="developer",
                channel=channel,
                thread_ts=thread_ts,
            ),
        ]

        return SlackThread(
            channel=channel,
            thread_ts=thread_ts,
            messages=messages,
        )