from unittest.mock import Mock

from qa_mcp.core.automation.execution_reporting_service import (
    AutomationExecutionReportingService,
)
from qa_mcp.models.execution_reporting import (
    AutomationExecutionReport,
)


def test_reporting_service_returns_report():
    history_service = Mock()

    expected = AutomationExecutionReport(
        total_executions=4,
        passed=2,
        failed=1,
        not_executed=1,
        error=0,
        pass_rate_percent=50.0,
        total_duration_seconds=10.0,
        average_duration_seconds=2.5,
        latest_execution_id="EX004",
        latest_status="NOT_EXECUTED",
    )

    history_service.report.return_value = expected

    service = AutomationExecutionReportingService(
        history_service
    )

    result = service.report()

    assert result == expected

    history_service.report.assert_called_once_with(
        automation_case_id=None
    )


def test_reporting_service_filters_by_automation_case():
    history_service = Mock()

    history_service.report.return_value = (
        AutomationExecutionReport(
            total_executions=2,
            passed=2,
            failed=0,
            not_executed=0,
            error=0,
            pass_rate_percent=100.0,
            total_duration_seconds=4.0,
            average_duration_seconds=2.0,
            latest_execution_id="EX002",
            latest_status="PASSED",
        )
    )

    service = AutomationExecutionReportingService(
        history_service
    )

    result = service.report(
        automation_case_id="AC001"
    )

    assert result.total_executions == 2
    assert result.passed == 2
    assert result.pass_rate_percent == 100.0

    history_service.report.assert_called_once_with(
        automation_case_id="AC001"
    )
