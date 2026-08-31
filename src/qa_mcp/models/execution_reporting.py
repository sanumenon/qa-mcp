from __future__ import annotations

from pydantic import BaseModel


class AutomationExecutionReport(BaseModel):
    """Aggregated report for persisted automation executions."""

    total_executions: int
    passed: int
    failed: int
    not_executed: int
    error: int
    pass_rate_percent: float
    total_duration_seconds: float
    average_duration_seconds: float
    latest_execution_id: str | None = None
    latest_status: str | None = None
