from qa_mcp.core.github.service import (
    GitHubService,
)

from qa_mcp.infrastructure.github.cloud_client import (
    GitHubCloudClient,
)


def create_github_service(
    config: dict,
) -> GitHubService | None:
    """Create GitHub service when GitHub is configured."""

    features = config.get(
        "features",
        {},
    )

    if not features.get(
        "github_connector",
        False,
    ):
        return None

    github_config = config.get(
        "github",
        {},
    )

    url = github_config.get(
        "url",
        "",
    )

    token = github_config.get(
        "token",
        "",
    )

    owner = github_config.get(
        "owner",
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

    if (
        not isinstance(owner, str)
        or not owner.strip()
    ):
        return None

    client = GitHubCloudClient(
        base_url=url,
        token=token,
    )

    return GitHubService(
        client
    )