from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_FILE = PROJECT_ROOT / "config" / "settings.yaml"

load_dotenv(PROJECT_ROOT / ".env")


def load_config() -> dict:
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    config["llm"]["provider"] = os.getenv(
        "LLM_PROVIDER",
        config["llm"].get("provider", "mock"),
    )
    return config
