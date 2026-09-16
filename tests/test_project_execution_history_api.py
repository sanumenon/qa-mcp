from types import SimpleNamespace

import pytest

from qa_mcp.infrastructure.sqlite_automation_execution_repository import (
    SQLiteAutomationExecutionRepository,
)


class FakeArtifactRepository:
    def __init__(self):
        self.projects = {
            "project-a": [
                {
                    "artifact_id": "artifact-a",
                    "automation_case_id": "case-a",
                }
            ],
            "project-b": [
                {
                    "artifact_id": "artifact-b",
                    "automation_case_id": "case-b",
                }
            ],
        }

    def list_for_project(self, project_id, limit=50):
        return self.projects.get(project_id, [])[:limit]


def execution(
    execution_id,
    artifact_id,
    case_id,
    status="PASSED",
):
    return SimpleNamespace(
        execution_id=execution_id,
        automation_artifact_id=artifact_id,
        automation_case_id=case_id,
        status=status,
        exit_code=0 if status == "PASSED" else 1,
        stdout="stdout",
        stderr="",
        duration_seconds=1.0,
        error=None,
    )


def test_project_execution_list_is_project_scoped(tmp_path):
    repository = SQLiteAutomationExecutionRepository(
        database_path=str(tmp_path / "qa.db")
    )
    artifact_repository = FakeArtifactRepository()

    repository.save(
        execution(
            "execution-a",
            "artifact-a",
            "case-a",
        )
    )
    repository.save(
        execution(
            "execution-b",
            "artifact-b",
            "case-b",
        )
    )

    results = repository.list_for_project(
        project_id="project-a",
        artifact_repository=artifact_repository,
    )

    assert [
        item.execution_id
        for item in results
    ] == ["execution-a"]


def test_project_execution_detail_cannot_cross_project(tmp_path):
    repository = SQLiteAutomationExecutionRepository(
        database_path=str(tmp_path / "qa.db")
    )
    artifact_repository = FakeArtifactRepository()

    repository.save(
        execution(
            "execution-b",
            "artifact-b",
            "case-b",
        )
    )

    result = repository.get_for_project(
        project_id="project-a",
        execution_id="execution-b",
        artifact_repository=artifact_repository,
    )

    assert result is None


def test_project_report_is_project_scoped(tmp_path):
    repository = SQLiteAutomationExecutionRepository(
        database_path=str(tmp_path / "qa.db")
    )
    artifact_repository = FakeArtifactRepository()

    repository.save(
        execution(
            "execution-a",
            "artifact-a",
            "case-a",
            status="PASSED",
        )
    )
    repository.save(
        execution(
            "execution-b",
            "artifact-b",
            "case-b",
            status="FAILED",
        )
    )

    report = repository.report_for_project(
        project_id="project-a",
        artifact_repository=artifact_repository,
    )

    assert report.total_executions == 1
    assert report.passed == 1
    assert report.failed == 0
    assert report.pass_rate_percent == 100.0


def test_project_failure_analysis_is_project_scoped(tmp_path):
    repository = SQLiteAutomationExecutionRepository(
        database_path=str(tmp_path / "qa.db")
    )
    artifact_repository = FakeArtifactRepository()

    repository.save(
        execution(
            "execution-a",
            "artifact-a",
            "case-a",
            status="FAILED",
        )
    )
    repository.save(
        execution(
            "execution-b",
            "artifact-b",
            "case-b",
            status="FAILED",
        )
    )

    analysis = repository.analyze_failures_for_project(
        project_id="project-a",
        artifact_repository=artifact_repository,
    )

    assert analysis.total_executions == 1
    assert analysis.total_failures == 1
    assert analysis.affected_automation_cases == ["case-a"]
