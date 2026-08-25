from qa_mcp.infrastructure.slack.client import (
    SlackClient,
)
from qa_mcp.models.schemas import (
    SlackChannel,
    SlackMessage,
    SlackSearchResult,
    SlackThread,
)


class SlackService:
    """Application service for read-only Slack operations."""

    def __init__(
        self,
        client: SlackClient,
    ):
        self.client = client

    def get_channel(
        self,
        channel: str,
    ) -> SlackChannel:
        """Retrieve Slack channel information."""

        return self.client.get_channel(
            channel
        )

    def get_messages(
        self,
        channel: str,
        limit: int = 50,
    ) -> list[SlackMessage]:
        """Retrieve recent Slack messages."""

        return self.client.get_messages(
            channel,
            limit=limit,
        )

    def search_messages(
        self,
        query: str,
        max_results: int = 50,
    ) -> SlackSearchResult:
        """Search Slack messages."""

        return self.client.search_messages(
            query,
            max_results=max_results,
        )

    def get_thread(
        self,
        channel: str,
        thread_ts: str,
    ) -> SlackThread:
        """Retrieve a Slack message thread."""

        return self.client.get_thread(
            channel,
            thread_ts,
        )