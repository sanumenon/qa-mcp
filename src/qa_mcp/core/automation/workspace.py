from pathlib import Path, PureWindowsPath
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

        self._validate_file_name(
            artifact.file_name
        )

        workspace_path = Path(
            tempfile.mkdtemp(
                prefix="qa-mcp-execution-",
                dir=self.root,
            )
        )

        file_path = workspace_path / artifact.file_name

        workspace_resolved = workspace_path.resolve()
        file_resolved = file_path.resolve()

        try:
            file_resolved.relative_to(
                workspace_resolved
            )
        except ValueError as exc:
            raise ValueError(
                "Unsafe automation artifact file name: "
                f"{artifact.file_name}"
            ) from exc

        file_path.write_text(
            artifact.code,
            encoding="utf-8",
        )

        self.path = workspace_path

        return workspace_path

    @staticmethod
    def _validate_file_name(
        file_name: str,
    ) -> None:
        """Reject paths that can escape or alter the workspace."""

        windows_path = PureWindowsPath(file_name)
        posix_path = Path(file_name)

        if (
            not file_name
            or not file_name.strip()
            or "\x00" in file_name
            or file_name != file_name.strip()
            or posix_path.is_absolute()
            or windows_path.is_absolute()
            or windows_path.drive
            or len(posix_path.parts) != 1
            or len(windows_path.parts) != 1
            or posix_path.name != file_name
            or windows_path.name != file_name
            or ":" in file_name
        ):
            raise ValueError(
                "Unsafe automation artifact file name: "
                f"{file_name}"
            )

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
