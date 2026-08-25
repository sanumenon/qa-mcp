from abc import ABC, abstractmethod

from qa_mcp.models.schemas import (
    SlackChannel,
    SlackMessage,
    SlackSearchResult,
    SlackThread,
)


class SlackClient(ABC):
    """Abstract Slack client."""

    @abstractmethod
    def get_channel(
        self,
        channel: str,
    ) -> SlackChannel:
        """Retrieve Slack channel information."""

        raise NotImplementedError

    @abstractmethod
    def get_messages(
        self,
        channel: str,
        limit: int = 50,
    ) -> list[SlackMessage]:
        """Retrieve recent messages from a Slack channel."""

        raise NotImplementedError

    @abstractmethod
    def search_messages(
        self,
        query: str,
        max_results: int = 50,
    ) -> SlackSearchResult:
        """Search Slack messages."""

        raise NotImplementedError

    @abstractmethod
    def get_thread(
        self,
        channel: str,
        thread_ts: str,
    ) -> SlackThread:
        """Retrieve a Slack message thread."""

        raise NotImplementedError