from qa_mcp.core.config import load_config


def test_github_configuration_defaults(monkeypatch):

    monkeypatch.delenv(
        "GITHUB_URL",
        raising=False,
    )

    monkeypatch.delenv(
        "GITHUB_TOKEN",
        raising=False,
    )

    monkeypatch.delenv(
        "GITHUB_OWNER",
        raising=False,
    )

    config = load_config()

    assert "github" in config

    assert (
        config["github"]["url"]
        == "https://api.github.com"
    )

    assert (
        config["github"]["token"]
        == ""
    )

    assert (
        config["github"]["owner"]
        == ""
    )

def test_github_connector_disabled_by_default():

    config = load_config()

    assert (
        config["features"]["github_connector"]
        is False
    )

def test_github_configuration_environment_overrides(
    monkeypatch,
):

    monkeypatch.setenv(
        "GITHUB_URL",
        "https://github.example.com/api/v3",
    )

    monkeypatch.setenv(
        "GITHUB_TOKEN",
        "test-token",
    )

    monkeypatch.setenv(
        "GITHUB_OWNER",
        "qa-team",
    )

    config = load_config()

    assert (
        config["github"]["url"]
        == "https://github.example.com/api/v3"
    )

    assert (
        config["github"]["token"]
        == "test-token"
    )

    assert (
        config["github"]["owner"]
        == "qa-team"
    )