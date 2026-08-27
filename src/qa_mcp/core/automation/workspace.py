from pathlib import Path
import tempfile

from qa_mcp.models.schemas import GeneratedAutomationArtifact


class AutomationWorkspace:
    """Create and manage an isolated automation execution workspace."""

    def __init__(
        self,
        root: str | None = None,
        keep_workspace: bool = False,
    ):
        self.root = root
        self.keep_workspace = keep_workspace
        self.path: Path | None = None

    def create(
        self,
        artifact: GeneratedAutomationArtifact,
    ) -> Path:
        """Create a workspace and write the automation artifact."""

        workspace_path = Path(
            tempfile.mkdtemp(
                prefix="qa-mcp-execution-",
                dir=self.root,
            )
        )

        file_path = workspace_path / artifact.file_name

        file_path.write_text(
            artifact.code,
            encoding="utf-8",
        )

        self.path = workspace_path

        return workspace_path

    def cleanup(self) -> None:
        """Remove the workspace unless retention was requested."""

        if self.keep_workspace:
            return

        if self.path is None:
            return

        for path in sorted(
            self.path.rglob("*"),
            reverse=True,
        ):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()

        self.path.rmdir()
        self.path = None