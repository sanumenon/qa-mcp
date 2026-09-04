from qa_mcp.infrastructure.sqlite_qa_workspace_artifact_repository import (
    SQLiteQAWorkspaceArtifactRepository,
)
from qa_mcp.models.schemas import GeneratedAutomationArtifact


def build_artifact():
    return GeneratedAutomationArtifact(
        id="GA-S9.13-001",
        automation_case_id="AC-S9.13-001",
        framework="Playwright",
        language="Python",
        file_name="test_reset_password.py",
        code="def test_reset_password(page):\n    pass",
    )


def test_workspace_artifact_repository_persists_artifact(
    tmp_path,
):
    repository = (
        SQLiteQAWorkspaceArtifactRepository(
            str(tmp_path / "workspace.db")
        )
    )

    artifact = build_artifact()

    repository.save(
        artifact=artifact,
        project_id="qa-project",
        test_case_id="TC-001",
        created_at="2026-09-04T10:00:00+00:00",
    )

    loaded = repository.get_for_project(
        project_id="qa-project",
        artifact_id="GA-S9.13-001",
    )

    assert loaded is not None
    assert loaded["artifact_id"] == (
        "GA-S9.13-001"
    )
    assert loaded["project_id"] == (
        "qa-project"
    )
    assert loaded["automation_case_id"] == (
        "AC-S9.13-001"
    )
    assert loaded["test_case_id"] == "TC-001"
    assert loaded["file_name"] == (
        "test_reset_password.py"
    )


def test_workspace_artifact_repository_is_project_scoped(
    tmp_path,
):
    repository = (
        SQLiteQAWorkspaceArtifactRepository(
            str(tmp_path / "workspace.db")
        )
    )

    repository.save(
        artifact=build_artifact(),
        project_id="qa-project",
        test_case_id="TC-001",
        created_at="2026-09-04T10:00:00+00:00",
    )

    assert (
        repository.get_for_project(
            project_id="other-project",
            artifact_id="GA-S9.13-001",
        )
        is None
    )


def test_workspace_artifact_repository_rejects_invalid_limit(
    tmp_path,
):
    repository = (
        SQLiteQAWorkspaceArtifactRepository(
            str(tmp_path / "workspace.db")
        )
    )

    try:
        repository.list_for_project(
            project_id="qa-project",
            limit=0,
        )
    except ValueError as exc:
        assert "greater than zero" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )