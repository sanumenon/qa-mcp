from dataclasses import dataclass


@dataclass(frozen=True)
class AutomationExecutionConfig:
    """Configuration for controlled automation execution."""

    timeout_seconds: int = 60
    workspace_root: str | None = None
    keep_workspace: bool = False

    def __post_init__(self) -> None:
        """Validate execution configuration."""

        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, int)
            or self.timeout_seconds <= 0
        ):
            raise ValueError(
                "Automation execution timeout must be "
                "a positive integer"
            )