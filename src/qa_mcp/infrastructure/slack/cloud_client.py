from typing import Any

import requests

from qa_mcp.infrastructure.slack.client import (
    SlackClient,
)

from qa_mcp.models.schemas import (
    SlackChannel,
    SlackMessage,
    SlackSearchResult,
    SlackThread,
)


class SlackCloudClient(SlackClient):
    """Slack Web API client."""

    def __init__(
        self,
        base_url: str,
        token: str,
    ):
        if not base_url.strip():
            raise ValueError(
                "Slack base URL cannot be empty"
            )

        if not token.strip():
            raise ValueError(
                "Slack token cannot be empty"
            )

        self.base_url = base_url.rstrip("/")
        self.token = token

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict:

        url = (
            f"{self.base_url}"
            f"{path}"
        )

        headers = {
            "Authorization": (
                f"Bearer {self.token}"
            ),
            "Content-Type": (
                "application/json"
            ),
        }

        response = requests.request(
            method,
            url,
            headers=headers,
            **kwargs,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok", False):

            error = data.get(
                "error",
                "unknown_error",
            )

            if error in {
                "invalid_auth",
                "not_authed",
            }:
                raise ValueError(
                    "Slack authentication failed"
                )

            if error in {
                "channel_not_found",
                "not_in_channel",
            }:
                raise ValueError(
                    "Slack channel not found"
                )

            raise ValueError(
                f"Slack API request failed: "
                f"{error}"
            )

        return data

    def get_channel(
        self,
        channel: str,
    ) -> SlackChannel:

        if not channel.strip():
            raise ValueError(
                "Slack channel cannot be empty"
            )

        data = self._request(
            "GET",
            "/conversations.info",
            params={
                "channel": channel,
            },
        )

        channel_data = data.get(
            "channel",
            {},
        )

        return SlackChannel(
            id=channel_data.get(
                "id",
                "",
            ),
            name=channel_data.get(
                "name",
                "",
            ),
            is_private=channel_data.get(
                "is_private",
                False,
            ),
            is_archived=channel_data.get(
                "is_archived",
                False,
            ),
            url=(
                f"https://slack.com/archives/"
                f"{channel_data.get('id', '')}"
            ),
        )

    def get_messages(
        self,
        channel: str,
        limit: int = 50,
    ) -> list[SlackMessage]:

        if not channel.strip():
            raise ValueError(
                "Slack channel cannot be empty"
            )

        data = self._request(
            "GET",
            "/conversations.history",
            params={
                "channel": channel,
                "limit": limit,
            },
        )

        messages = []

        for item in data.get(
            "messages",
            [],
        ):

            messages.append(
                SlackMessage(
                    ts=item.get(
                        "ts",
                        "",
                    ),
                    text=item.get(
                        "text",
                        "",
                    ),
                    user=item.get(
                        "user",
                        "",
                    ),
                    channel=channel,
                    thread_ts=item.get(
                        "thread_ts",
                        "",
                    ),
                )
            )

        return messages

    def search_messages(
        self,
        query: str,
        max_results: int = 50,
    ) -> SlackSearchResult:

        if not query.strip():
            raise ValueError(
                "Slack search query cannot be empty"
            )

        data = self._request(
            "GET",
            "/search.messages",
            params={
                "query": query,
                "count": max_results,
            },
        )

        search_data = data.get(
            "messages",
            {},
        )

        messages = []

        for item in search_data.get(
            "matches",
            [],
        ):

            channel_data = item.get(
                "channel",
                {},
            )

            messages.append(
                SlackMessage(
                    ts=item.get(
                        "ts",
                        "",
                    ),
                    text=item.get(
                        "text",
                        "",
                    ),
                    user=item.get(
                        "username",
                        "",
                    ),
                    channel=channel_data.get(
                        "name",
                        "",
                    ),
                    url=item.get(
                        "permalink",
                        "",
                    ),
                )
            )

        return SlackSearchResult(
            messages=messages,
            total=search_data.get(
                "total",
                len(messages),
            ),
        )

    def get_thread(
        self,
        channel: str,
        thread_ts: str,
    ) -> SlackThread:

        if not channel.strip():
            raise ValueError(
                "Slack channel cannot be empty"
            )

        if not thread_ts.strip():
            raise ValueError(
                "Slack thread timestamp "
                "cannot be empty"
            )

        data = self._request(
            "GET",
            "/conversations.replies",
            params={
                "channel": channel,
                "ts": thread_ts,
            },
        )

        messages = []

        for item in data.get(
            "messages",
            [],
        ):

            messages.append(
                SlackMessage(
                    ts=item.get(
                        "ts",
                        "",
                    ),
                    text=item.get(
                        "text",
                        "",
                    ),
                    user=item.get(
                        "user",
                        "",
                    ),
                    channel=channel,
                    thread_ts=item.get(
                        "thread_ts",
                        thread_ts,
                    ),
                )
            )

        return SlackThread(
            channel=channel,
            thread_ts=thread_ts,
            messages=messages,
        )