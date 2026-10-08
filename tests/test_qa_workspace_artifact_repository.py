from qa_mcp.core.automation.code_generation_service import (
    AutomationCodeGenerationService,
)
from qa_mcp.infrastructure.sqlite_qa_workspace_artifact_repository import (
    SQLiteQAWorkspaceArtifactRepository,
)
from qa_mcp.models.schemas import (
    AutomationCase,
    GeneratedAutomationArtifact,
)


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


def test_generated_artifacts_with_distinct_ids_coexist_across_projects(
    tmp_path,
):
    repository = SQLiteQAWorkspaceArtifactRepository(
        str(tmp_path / "workspace.db")
    )
    service = AutomationCodeGenerationService()

    artifact_a = service.generate(
        AutomationCase(
            id="AC-A",
            test_case_id="TC-A",
            title="Artifact A",
            automation_type="UI",
            framework="Playwright",
            priority="High",
            confidence="High",
            preconditions=[],
            test_data=[],
            steps=["click: #artifact-a"],
            assertions=["visible: #artifact-a"],
            limitations=[],
        )
    )
    artifact_b = service.generate(
        AutomationCase(
            id="AC-B",
            test_case_id="TC-B",
            title="Artifact B",
            automation_type="UI",
            framework="Playwright",
            priority="High",
            confidence="High",
            preconditions=[],
            test_data=[],
            steps=["click: #artifact-b"],
            assertions=["visible: #artifact-b"],
            limitations=[],
        )
    )
    artifact_other_project = service.generate(
        AutomationCase(
            id="AC-C",
            test_case_id="TC-C",
            title="Other Project Artifact",
            automation_type="UI",
            framework="Playwright",
            priority="High",
            confidence="High",
            preconditions=[],
            test_data=[],
            steps=["click: #artifact-c"],
            assertions=["visible: #artifact-c"],
            limitations=[],
        )
    )

    assert len(
        {
            artifact_a.id,
            artifact_b.id,
            artifact_other_project.id,
        }
    ) == 3

    legacy_artifact = GeneratedAutomationArtifact(
        id="GA001",
        automation_case_id="AC-LEGACY",
        framework="Playwright",
        language="Python",
        file_name="test_legacy.py",
        code="print('legacy artifact')",
    )

    for artifact, project_id, test_case_id in (
        (artifact_a, "project-a", "TC-A"),
        (artifact_b, "project-a", "TC-B"),
        (artifact_other_project, "project-b", "TC-C"),
        (legacy_artifact, "project-a", "TC-LEGACY"),
    ):
        repository.save(
            artifact=artifact,
            project_id=project_id,
            test_case_id=test_case_id,
            created_at="2026-10-08T00:00:00+00:00",
        )

    project_a_artifacts = repository.list_for_project(
        "project-a"
    )
    project_b_artifacts = repository.list_for_project(
        "project-b"
    )

    assert {item["artifact_id"] for item in project_a_artifacts} == {
        artifact_a.id,
        artifact_b.id,
        "GA001",
    }
    assert {item["artifact_id"] for item in project_b_artifacts} == {
        artifact_other_project.id,
    }
    assert repository.get_for_project(
        "project-a", artifact_a.id
    )["code"] == artifact_a.code
    assert repository.get_for_project(
        "project-a", artifact_b.id
    )["code"] == artifact_b.code
    assert repository.get_for_project(
        "project-b", artifact_other_project.id
    )["code"] == artifact_other_project.code
    assert repository.get_for_project(
        "project-a", "GA001"
    )["code"] == "print('legacy artifact')"
