from __future__ import annotations

from qa_mcp.core.automation.execution_history_service import (
    AutomationExecutionHistoryService,
)
from qa_mcp.models.execution_reporting import (
    AutomationExecutionReport,
)


class AutomationExecutionReportingService:
    """Generate aggregated automation execution reports."""

    def __init__(
        self,
        history_service: AutomationExecutionHistoryService,
    ):
        self.history_service = history_service

    def report(
        self,
        automation_case_id: str | None = None,
    ) -> AutomationExecutionReport:
        return self.history_service.report(
            automation_case_id=automation_case_id,
        )
