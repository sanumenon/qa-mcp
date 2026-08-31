from __future__ import annotations

from qa_mcp.infrastructure.sqlite_automation_execution_repository import (
    SQLiteAutomationExecutionRepository,
)
from qa_mcp.models.execution_failure_analysis import (
    AutomationExecutionFailureAnalysis,
)


class AutomationExecutionFailureAnalysisService:
    """Analyze persisted automation execution failures."""

    def __init__(
        self,
        repository: SQLiteAutomationExecutionRepository | None = None,
    ):
        self.repository = (
            repository
            if repository is not None
            else SQLiteAutomationExecutionRepository()
        )

    def analyze(
        self,
        automation_case_id: str | None = None,
        limit: int = 50,
    ) -> AutomationExecutionFailureAnalysis:
        return self.repository.analyze_failures(
            automation_case_id=automation_case_id,
            limit=limit,
        )
