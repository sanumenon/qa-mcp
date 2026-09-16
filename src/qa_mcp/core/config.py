from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_FILE = PROJECT_ROOT / "config" / "settings.yaml"

load_dotenv(PROJECT_ROOT / ".env")


def resolve_base_url() -> str:
    environment = os.getenv(
        "DEFAULT_TEST_ENV",
        "qa",
    ).strip().lower()

    base_urls = {
        "qa": os.getenv("QA_BASE_URL", ""),
        "stage": os.getenv("STAGE_BASE_URL", ""),
        "staging": os.getenv("STAGE_BASE_URL", ""),
        "prod": os.getenv("PROD_BASE_URL", ""),
        "production": os.getenv("PROD_BASE_URL", ""),
    }

    base_url = base_urls.get(environment, "").strip()

    if not base_url:
        raise ValueError(
            f"No base URL configured for test environment: {environment}"
        )

    return base_url.rstrip("/")


def load_config() -> dict:
    with CONFIG_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = yaml.safe_load(file) or {}

    config["llm"]["provider"] = os.getenv(
        "LLM_PROVIDER",
        config["llm"].get(
            "provider",
            "mock",
        ),
    )

    config.setdefault("jira", {})

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

    config.setdefault("github", {})

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

    config.setdefault("slack", {})

    config["slack"]["url"] = os.getenv(
        "SLACK_URL",
        config["slack"].get(
            "url",
            "https://slack.com/api",
        ),
    )

    config["slack"]["token"] = os.getenv(
        "SLACK_TOKEN",
        config["slack"].get(
            "token",
            "",
        ),
    )

    config["slack"]["default_channel"] = os.getenv(
        "SLACK_DEFAULT_CHANNEL",
        config["slack"].get(
            "default_channel",
            "",
        ),
    )

    config.setdefault("automation_execution", {})

    config["automation_execution"]["base_url"] = resolve_base_url()

    config["automation_execution"]["timeout_seconds"] = int(
        os.getenv(
            "QA_AUTOMATION_TIMEOUT_SECONDS",
            config["automation_execution"].get(
                "timeout_seconds",
                60,
            ),
        )
    )

    config["automation_execution"]["workspace_root"] = os.getenv(
        "QA_AUTOMATION_WORKSPACE_ROOT",
        config["automation_execution"].get(
            "workspace_root",
            "",
        ),
    )

    config["automation_execution"]["keep_workspace"] = os.getenv(
        "QA_AUTOMATION_KEEP_WORKSPACE",
        str(
            config["automation_execution"].get(
                "keep_workspace",
                False,
            )
        ),
    ).lower() in {"1", "true", "yes", "on"}

    return config