from qa_mcp.core.jira.service import JiraService
from qa_mcp.infrastructure.jira.cloud_client import (
    JiraCloudClient,
)


def create_jira_service(
    config: dict,
) -> JiraService | None:
    """Create Jira service when Jira is configured."""

    features = config.get(
        "features",
        {},
    )

    if not features.get(
        "jira_connector",
        False,
    ):
        return None

    jira_config = config.get(
        "jira",
        {},
    )

    url = jira_config.get(
        "url",
        "",
    )

    email = jira_config.get(
        "email",
        "",
    )

    api_token = jira_config.get(
        "api_token",
        "",
    )

    if (
        not url.strip()
        or not email.strip()
        or not api_token.strip()
    ):
        return None

    client = JiraCloudClient(
        base_url=url,
        email=email,
        api_token=api_token,
    )

    return JiraService(
        client
    )