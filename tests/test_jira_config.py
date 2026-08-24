from qa_mcp.core.config import load_config


def test_jira_configuration_defaults(
    monkeypatch,
):

    monkeypatch.delenv(
        "JIRA_URL",
        raising=False,
    )

    monkeypatch.delenv(
        "JIRA_EMAIL",
        raising=False,
    )

    monkeypatch.delenv(
        "JIRA_API_TOKEN",
        raising=False,
    )

    config = load_config()

    assert "jira" in config

    assert (
        config["jira"]["url"]
        == ""
    )

    assert (
        config["jira"]["email"]
        == ""
    )

    assert (
        config["jira"]["api_token"]
        == ""
    )

def test_jira_configuration_from_environment(
    monkeypatch,
):

    monkeypatch.setenv(
        "JIRA_URL",
        "https://example.atlassian.net",
    )

    monkeypatch.setenv(
        "JIRA_EMAIL",
        "qa@example.com",
    )

    monkeypatch.setenv(
        "JIRA_API_TOKEN",
        "test-token",
    )

    config = load_config()

    assert (
        config["jira"]["url"]
        == "https://example.atlassian.net"
    )

    assert (
        config["jira"]["email"]
        == "qa@example.com"
    )

    assert (
        config["jira"]["api_token"]
        == "test-token"
    )

def test_jira_configuration_reads_environment(
    monkeypatch,
):

    monkeypatch.setenv(
        "JIRA_URL",
        "https://env-test.atlassian.net",
    )

    monkeypatch.setenv(
        "JIRA_EMAIL",
        "qa@example.com",
    )

    monkeypatch.setenv(
        "JIRA_API_TOKEN",
        "test-token",
    )

    config = load_config()

    assert (
        config["jira"]["url"]
        == "https://env-test.atlassian.net"
    )

    assert (
        config["jira"]["email"]
        == "qa@example.com"
    )

    assert (
        config["jira"]["api_token"]
        == "test-token"
    )