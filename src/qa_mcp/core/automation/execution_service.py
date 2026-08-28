import sys

from qa_mcp.core.automation.execution_config import (
    AutomationExecutionConfig,
)
from qa_mcp.core.automation.execution_runner import (
    AutomationExecutionRunner,
)
from qa_mcp.core.automation.workspace import (
    AutomationWorkspace,
)
from qa_mcp.models.schemas import (
    AutomationExecutionResult,
    GeneratedAutomationArtifact,
)


class AutomationExecutionService:
    """Execute generated automation artifacts."""

    def __init__(
        self,
        config: AutomationExecutionConfig | None = None,
        runner: AutomationExecutionRunner | None = None,
    ):
        self.config = (
            config
            if config is not None
            else AutomationExecutionConfig()
        )

        self.runner = (
            runner
            if runner is not None
            else AutomationExecutionRunner()
        )

    def _build_command(
        self,
        artifact: GeneratedAutomationArtifact,
    ) -> list[str]:
        """Build the controlled command used to execute an automation artifact."""

        if artifact.framework.lower() != "playwright":
            raise ValueError(
                "Unsupported automation framework: "
                f"{artifact.framework}"
            )

        if (
            not artifact.file_name
            or artifact.file_name.strip() != artifact.file_name
            or artifact.file_name in {".", ".."}
            or "/" in artifact.file_name
            or "\\" in artifact.file_name
        ):
            raise ValueError(
                "Unsafe automation artifact filename: "
                f"{artifact.file_name}"
            )

        return [
            sys.executable,
            "-m",
            "pytest",
            artifact.file_name,
        ]

    def execute(
        self,
        artifact: GeneratedAutomationArtifact,
    ) -> AutomationExecutionResult:
        """Execute an automation artifact."""

        if not artifact.code.strip():
            raise ValueError(
                "Automation artifact must contain code"
            )

        if not artifact.framework:
            raise ValueError(
                "Automation artifact must specify a framework"
            )

        if artifact.framework.lower() != "playwright":
            raise ValueError(
                "Unsupported automation framework: "
                f"{artifact.framework}"
            )

        workspace = AutomationWorkspace(
            root=self.config.workspace_root,
            keep_workspace=self.config.keep_workspace,
        )

        workspace_path = workspace.create(
            artifact
        )

        try:
            command = self._build_command(artifact)

            process_result = self.runner.run(
                command=command,
                cwd=str(workspace_path),
                timeout_seconds=(
                    self.config.timeout_seconds
                ),
            )

            if process_result.timed_out:
                status = "TIMEOUT"
            elif process_result.error is not None:
                status = "ERROR"
            elif process_result.exit_code == 0:
                status = "PASSED"
            else:
                status = "FAILED"

            return AutomationExecutionResult(
                execution_id="EX001",
                automation_artifact_id=artifact.id,
                automation_case_id=artifact.automation_case_id,
                status=status,
                exit_code=process_result.exit_code,
                stdout=process_result.stdout,
                stderr=process_result.stderr,
                duration_seconds=(
                    process_result.duration_seconds
                ),
                error=process_result.error,
            )

        finally:
            workspace.cleanup()