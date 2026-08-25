from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_FILE = PROJECT_ROOT / "config" / "settings.yaml"

load_dotenv(PROJECT_ROOT / ".env")


def load_config() -> dict:
    with CONFIG_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        config = yaml.safe_load(
            file
        ) or {}

    config["llm"]["provider"] = os.getenv(
        "LLM_PROVIDER",
        config["llm"].get(
            "provider",
            "mock",
        ),
    )

    config.setdefault(
        "jira",
        {}
    )

    config["jira"]["url"] = os.getenv(
        "JIRA_URL",
        config["jira"].get(
            "url",
            "",
        ),
    )

    config["jira"]["email"] = os.getenv(
        "JIRA_EMAIL",
        config["jira"].get(
            "email",
            "",
        ),
    )

    config["jira"]["api_token"] = os.getenv(
        "JIRA_API_TOKEN",
        config["jira"].get(
            "api_token",
            "",
        ),
    )

    config.setdefault(
        "github",
        {}
    )

    config["github"]["url"] = os.getenv(
        "GITHUB_URL",
        config["github"].get(
            "url",
            "https://api.github.com",
        ),
    )

    config["github"]["token"] = os.getenv(
        "GITHUB_TOKEN",
        config["github"].get(
            "token",
            "",
        ),
    )

    config["github"]["owner"] = os.getenv(
        "GITHUB_OWNER",
        config["github"].get(
            "owner",
            "",
        ),
    )

    return config