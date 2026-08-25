from qa_mcp.core.slack.service import (
    SlackService,
)

from qa_mcp.infrastructure.slack.cloud_client import (
    SlackCloudClient,
)


def create_slack_service(
    config: dict,
) -> SlackService | None:
    """Create Slack service when Slack is configured."""

    features = config.get(
        "features",
        {},
    )

    if not features.get(
        "slack_connector",
        False,
    ):
        return None

    slack_config = config.get(
        "slack",
        {},
    )

    url = slack_config.get(
        "url",
        "",
    )

    token = slack_config.get(
        "token",
        "",
    )

    if (
        not isinstance(url, str)
        or not url.strip()
    ):
        return None

    if (
        not isinstance(token, str)
        or not token.strip()
    ):
        return None

    client = SlackCloudClient(
        base_url=url,
        token=token,
    )

    return SlackService(
        client
    )