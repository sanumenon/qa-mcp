from pathlib import Path

import pytest

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


@pytest.mark.parametrize(
    "file_name",
    [
        "../outside.py",
        "../../outside.py",
        "tests/test_login.py",
        "/tmp/outside.py",
        r"..\outside.py",
        r"..\..\outside.py",
        r"C:\temp\outside.py",
        r"C:outside.py",
    ],
)
def test_workspace_rejects_unsafe_file_names(file_name):

    workspace = AutomationWorkspace()

    with pytest.raises(
        ValueError,
        match="Unsafe automation artifact file name",
    ):
        workspace.create(
            build_artifact(file_name=file_name)
        )

    assert workspace.path is None


@pytest.mark.parametrize(
    "file_name",
    [
        "",
        "   ",
        ".",
        "..",
    ],
)
def test_workspace_rejects_invalid_file_names(file_name):

    workspace = AutomationWorkspace()

    with pytest.raises(
        ValueError,
        match="Unsafe automation artifact file name",
    ):
        workspace.create(
            build_artifact(file_name=file_name)
        )

    assert workspace.path is None


def test_workspace_writes_only_inside_created_workspace():

    workspace = AutomationWorkspace()

    path = workspace.create(
        build_artifact(file_name="test_login.py")
    )

    try:
        artifact_path = path / "test_login.py"

        assert artifact_path.exists()
        assert artifact_path.parent == path
        assert artifact_path.resolve().parent == path.resolve()
    finally:
        workspace.cleanup()


def test_workspace_rejects_path_that_escapes_workspace(tmp_path):

    workspace = AutomationWorkspace(
        root=str(tmp_path)
    )

    with pytest.raises(
        ValueError,
        match="Unsafe automation artifact file name",
    ):
        workspace.create(
            build_artifact(
                file_name="../outside.py"
            )
        )

    assert not (tmp_path / "outside.py").exists()
    assert workspace.path is None
