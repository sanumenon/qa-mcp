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
