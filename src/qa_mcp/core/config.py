from pathlib import Path
import os
import json
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
    config.setdefault("application", {})
    config["application"]["environment"] = os.getenv(
        "QA_ENVIRONMENT", config["application"].get("environment", "local")
    )

    config["llm"]["provider"] = os.getenv(
        "LLM_PROVIDER",
        config["llm"].get(
            "provider",
            "mock",
        ),
    )

    config["llm"]["connect_timeout_seconds"] = int(
        os.getenv(
            "BEDROCK_CONNECT_TIMEOUT_SECONDS",
            config["llm"].get(
                "connect_timeout_seconds",
                60,
            ),
        )
    )

    config["llm"]["read_timeout_seconds"] = int(
        os.getenv(
            "BEDROCK_READ_TIMEOUT_SECONDS",
            config["llm"].get(
                "read_timeout_seconds",
                180,
            ),
        )
    )

    config["llm"]["retry_mode"] = os.getenv(
        "BEDROCK_RETRY_MODE",
        config["llm"].get(
            "retry_mode",
            "standard",
        ),
    )

    config["llm"]["max_attempts"] = int(
        os.getenv(
            "BEDROCK_MAX_ATTEMPTS",
            config["llm"].get(
                "max_attempts",
                1,
            ),
        )
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

    config.setdefault("auth", {})
    config["auth"].update(
        {
            "mode": os.getenv(
                "QA_AUTH_MODE", config["auth"].get("mode", "development")
            ).strip().lower(),
            "google_client_id": os.getenv("GOOGLE_OIDC_CLIENT_ID", ""),
            "google_client_secret": os.getenv("GOOGLE_OIDC_CLIENT_SECRET", ""),
            "redirect_uri": os.getenv("GOOGLE_OIDC_REDIRECT_URI", ""),
            "workspace_domain": os.getenv("GOOGLE_WORKSPACE_DOMAIN", "").strip().lower(),
            "session_secret": os.getenv("QA_SESSION_SECRET", ""),
            "session_max_age_seconds": int(
                os.getenv(
                    "QA_SESSION_MAX_AGE_SECONDS",
                    str(config["auth"].get("session_max_age_seconds", 28800)),
                )
            ),
            "cookie_secure": os.getenv(
                "QA_SESSION_COOKIE_SECURE",
                "true" if config.get("application", {}).get("environment") == "production" else "false",
            ).strip().lower() in {"1", "true", "yes"},
            "global_admin_subjects": [
                value.strip()
                for value in os.getenv("QA_GLOBAL_ADMIN_SUBJECTS", "").split(",")
                if value.strip()
            ],
        }
    )
    try:
        config["auth"]["legacy_project_owners"] = json.loads(
            os.getenv("QA_LEGACY_PROJECT_OWNERS", "{}")
        )
    except json.JSONDecodeError as exc:
        raise ValueError("QA_LEGACY_PROJECT_OWNERS must be a JSON object") from exc
    if not isinstance(config["auth"]["legacy_project_owners"], dict):
        raise ValueError("QA_LEGACY_PROJECT_OWNERS must be a JSON object")
    if any(
        not isinstance(project_id, str)
        or not project_id.strip()
        or not isinstance(subject, str)
        or not subject.strip()
        for project_id, subject in config["auth"]["legacy_project_owners"].items()
    ):
        raise ValueError(
            "QA_LEGACY_PROJECT_OWNERS must map non-empty project IDs to Google subject IDs"
        )

    config.setdefault("database", {})
    config["database"]["path"] = os.getenv(
        "QA_DATABASE_PATH", config["database"].get("path", "data/qa_mcp.db")
    )
    os.environ.setdefault("QA_DATABASE_PATH", config["database"]["path"])
    config["database"]["backup_directory"] = os.getenv(
        "QA_BACKUP_DIRECTORY", config["database"].get("backup_directory", "data/backups")
    )
    config["database"]["backup_retention"] = int(
        os.getenv("QA_BACKUP_RETENTION", str(config["database"].get("backup_retention", 14)))
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
