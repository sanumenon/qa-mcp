from qa_mcp.core.config import load_config


def test_slack_configuration_defaults():

    config = load_config()

    assert "slack" in config

    assert (
        config["slack"]["url"]
        == "https://slack.com/api"
    )

    assert (
        config["slack"]["token"]
        == ""
    )

    assert (
        config["slack"]["default_channel"]
        == ""
    )


def test_slack_connector_disabled_by_default():

    config = load_config()

    assert (
        config["features"]["slack_connector"]
        is False
    )


def test_slack_configuration_environment_overrides(
    monkeypatch,
):

    monkeypatch.setenv(
        "SLACK_URL",
        "https://slack.example.com/api",
    )

    monkeypatch.setenv(
        "SLACK_TOKEN",
        "test-token",
    )

    monkeypatch.setenv(
        "SLACK_DEFAULT_CHANNEL",
        "qa-channel",
    )

    config = load_config()

    assert (
        config["slack"]["url"]
        == "https://slack.example.com/api"
    )

    assert (
        config["slack"]["token"]
        == "test-token"
    )

    assert (
        config["slack"]["default_channel"]
        == "qa-channel"
    )