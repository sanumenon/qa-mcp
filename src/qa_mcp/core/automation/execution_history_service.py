from __future__ import annotations

from qa_mcp.infrastructure.sqlite_automation_execution_repository import (
    SQLiteAutomationExecutionRepository,
)
from qa_mcp.models.schemas import AutomationExecutionResult


class AutomationExecutionHistoryService:
    """Application service for automation execution history."""

    def __init__(
        self,
        repository: (
            SQLiteAutomationExecutionRepository | None
        ) = None,
    ):
        self.repository = (
            repository
            if repository is not None
            else SQLiteAutomationExecutionRepository()
        )

    def save(
        self,
        result: AutomationExecutionResult,
    ) -> AutomationExecutionResult:
        return self.repository.save(result)

    def get(
        self,
        execution_id: str,
    ) -> AutomationExecutionResult | None:
        return self.repository.get(execution_id)

    def list(
        self,
        automation_case_id: str | None = None,
        limit: int = 50,
    ) -> list[AutomationExecutionResult]:
        return self.repository.list(
            automation_case_id=automation_case_id,
            limit=limit,
        )

    def report(
        self,
        automation_case_id: str | None = None,
    ):
        return self.repository.report(
            automation_case_id=automation_case_id,
        )

    def list_for_project(
        self,
        project_id: str,
        artifact_repository,
        limit: int = 50,
    ) -> list[AutomationExecutionResult]:
        return self.repository.list_for_project(
            project_id=project_id,
            artifact_repository=artifact_repository,
            limit=limit,
        )

    def get_for_project(
        self,
        project_id: str,
        execution_id: str,
        artifact_repository,
    ) -> AutomationExecutionResult | None:
        return self.repository.get_for_project(
            project_id=project_id,
            execution_id=execution_id,
            artifact_repository=artifact_repository,
        )

    def report_for_project(
        self,
        project_id: str,
        artifact_repository,
    ):
        return self.repository.report_for_project(
            project_id=project_id,
            artifact_repository=artifact_repository,
        )

    def analyze_failures_for_project(
        self,
        project_id: str,
        artifact_repository,
        limit: int = 50,
    ):
        return self.repository.analyze_failures_for_project(
            project_id=project_id,
            artifact_repository=artifact_repository,
            limit=limit,
        )
