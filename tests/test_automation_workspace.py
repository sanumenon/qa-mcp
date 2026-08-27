from pathlib import Path

from qa_mcp.core.automation.workspace import (
    AutomationWorkspace,
)
from qa_mcp.models.schemas import (
    GeneratedAutomationArtifact,
)


def build_artifact(**overrides):
    data = {
        "id": "GA001",
        "automation_case_id": "AC001",
        "framework": "Playwright",
        "language": "Python",
        "file_name": "test_successful_login.py",
        "code": (
            "def test_successful_login(page):\n"
            "    pass\n"
        ),
    }

    data.update(overrides)

    return GeneratedAutomationArtifact(**data)


def test_workspace_writes_generated_artifact():

    workspace = AutomationWorkspace()

    path = workspace.create(
        build_artifact()
    )

    try:
        artifact_path = (
            path / "test_successful_login.py"
        )

        assert path.exists()
        assert path.is_dir()

        assert artifact_path.exists()
        assert artifact_path.read_text(
            encoding="utf-8"
        ) == (
            "def test_successful_login(page):\n"
            "    pass\n"
        )

    finally:
        workspace.cleanup()


def test_workspace_cleanup_removes_workspace():

    workspace = AutomationWorkspace()

    path = workspace.create(
        build_artifact()
    )

    assert path.exists()

    workspace.cleanup()

    assert not path.exists()


def test_workspace_can_be_retained():

    workspace = AutomationWorkspace(
        keep_workspace=True
    )

    path = workspace.create(
        build_artifact()
    )

    workspace.cleanup()

    try:
        assert path.exists()
        assert (
            path / "test_successful_login.py"
        ).exists()
    finally:
        for child in path.rglob("*"):
            if child.is_file():
                child.unlink()

        path.rmdir()