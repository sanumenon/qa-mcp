from dataclasses import dataclass


@dataclass(frozen=True)
class AutomationExecutionConfig:
    """Configuration for controlled automation execution."""

    timeout_seconds: int = 60
    workspace_root: str | None = None
    keep_workspace: bool = False