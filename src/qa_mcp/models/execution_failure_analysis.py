from __future__ import annotations

from pydantic import BaseModel


class AutomationExecutionFailure(BaseModel):
    """Structured information about a failed automation execution."""

    execution_id: str
    automation_artifact_id: str
    automation_case_id: str
    status: str
    exit_code: int | None = None
    message: str
    stderr: str = ""
    duration_seconds: float = 0.0


class AutomationExecutionFailureAnalysis(BaseModel):
    """Aggregated failure analysis for persisted automation executions."""

    total_executions: int
    failed_executions: int
    error_executions: int
    total_failures: int
    failure_rate_percent: float
    affected_automation_cases: list[str]
    latest_failure_execution_id: str | None = None
    latest_failure_status: str | None = None
    failures: list[AutomationExecutionFailure]
