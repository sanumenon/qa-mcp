from unittest.mock import Mock

from qa_mcp.core.automation.execution_failure_analysis_service import (
    AutomationExecutionFailureAnalysisService,
)
from qa_mcp.models.execution_failure_analysis import (
    AutomationExecutionFailureAnalysis,
)


def test_failure_analysis_service_returns_analysis():
    repository = Mock()

    expected = AutomationExecutionFailureAnalysis(
        total_executions=4,
        failed_executions=1,
        error_executions=1,
        total_failures=2,
        failure_rate_percent=50.0,
        affected_automation_cases=["AC001", "AC002"],
        latest_failure_execution_id="EX004",
        latest_failure_status="ERROR",
        failures=[],
    )

    repository.analyze_failures.return_value = expected

    service = AutomationExecutionFailureAnalysisService(
        repository=repository
    )

    result = service.analyze(
        automation_case_id="AC001",
        limit=10,
    )

    assert result == expected

    repository.analyze_failures.assert_called_once_with(
        automation_case_id="AC001",
        limit=10,
    )


def test_failure_analysis_service_uses_defaults():
    repository = Mock()
    expected = AutomationExecutionFailureAnalysis(
        total_executions=0,
        failed_executions=0,
        error_executions=0,
        total_failures=0,
        failure_rate_percent=0.0,
        affected_automation_cases=[],
        failures=[],
    )
    repository.analyze_failures.return_value = expected

    service = AutomationExecutionFailureAnalysisService(
        repository=repository
    )

    result = service.analyze()

    assert result == expected

    repository.analyze_failures.assert_called_once_with(
        automation_case_id=None,
        limit=50,
    )
