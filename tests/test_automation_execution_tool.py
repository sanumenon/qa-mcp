from unittest.mock import Mock

from qa_mcp.models.schemas import (
    AutomationExecutionResult,
)
from qa_mcp import server


def test_execute_automation_code_tool():

    mock_service = Mock()

    mock_service.execute.return_value = (
        AutomationExecutionResult(
            execution_id="EX001",
            automation_artifact_id="GA001",
            automation_case_id="AC001",
            status="NOT_EXECUTED",
            exit_code=None,
            stdout="",
            stderr="",
            duration_seconds=0.0,
            error=None,
        )
    )

    original_service = (
        server.automation_execution_service
    )

    server.automation_execution_service = (
        mock_service
    )

    try:
        result = server.execute_automation_code(
            artifact={
                "id": "GA001",
                "automation_case_id": "AC001",
                "framework": "Playwright",
                "language": "Python",
                "file_name": "test_successful_login.py",
                "code": (
                    "def test_successful_login(page):\n"
                    "    pass"
                ),
            }
        )

        assert result["execution_id"] == "EX001"
        assert result["automation_artifact_id"] == "GA001"
        assert result["automation_case_id"] == "AC001"
        assert result["status"] == "NOT_EXECUTED"

        mock_service.execute.assert_called_once()

    finally:
        server.automation_execution_service = (
            original_service
        )

def test_execute_automation_code_tool_persists_result():
    execution_service = Mock()
    history_service = Mock()

    execution_service.execute.return_value = (
        AutomationExecutionResult(
            execution_id="EX-S10-TOOL-001",
            automation_artifact_id="GA001",
            automation_case_id="AC001",
            status="PASSED",
            exit_code=0,
            stdout="1 passed",
            stderr="",
            duration_seconds=1.25,
            error=None,
        )
    )

    original_execution_service = (
        server.automation_execution_service
    )
    original_history_service = (
        server.automation_execution_history_service
    )

    server.automation_execution_service = (
        execution_service
    )
    server.automation_execution_history_service = (
        history_service
    )

    try:
        result = server.execute_automation_code(
            artifact={
                "id": "GA001",
                "automation_case_id": "AC001",
                "framework": "Playwright",
                "language": "Python",
                "file_name": "test_successful_login.py",
                "code": (
                    "def test_successful_login(page):\n"
                    "    pass"
                ),
            }
        )

        assert result["execution_id"] == "EX-S10-TOOL-001"
        assert result["status"] == "PASSED"

        execution_service.execute.assert_called_once()
        history_service.save.assert_called_once_with(
            execution_service.execute.return_value
        )

    finally:
        server.automation_execution_service = (
            original_execution_service
        )
        server.automation_execution_history_service = (
            original_history_service
        )


def test_get_automation_execution_tool():
    history_service = Mock()

    history_service.get.return_value = (
        AutomationExecutionResult(
            execution_id="EX-S10-GET-001",
            automation_artifact_id="GA001",
            automation_case_id="AC001",
            status="PASSED",
            exit_code=0,
            stdout="1 passed",
            stderr="",
            duration_seconds=1.25,
            error=None,
        )
    )

    original_history_service = (
        server.automation_execution_history_service
    )

    server.automation_execution_history_service = (
        history_service
    )

    try:
        result = server.get_automation_execution(
            "EX-S10-GET-001"
        )

        assert result["execution_id"] == "EX-S10-GET-001"
        assert result["automation_case_id"] == "AC001"
        assert result["status"] == "PASSED"

        history_service.get.assert_called_once_with(
            "EX-S10-GET-001"
        )

    finally:
        server.automation_execution_history_service = (
            original_history_service
        )


def test_get_automation_execution_tool_raises_when_missing():
    history_service = Mock()
    history_service.get.return_value = None

    original_history_service = (
        server.automation_execution_history_service
    )

    server.automation_execution_history_service = (
        history_service
    )

    try:
        try:
            server.get_automation_execution(
                "EX-S10-MISSING"
            )
        except ValueError as exc:
            assert (
                str(exc)
                == "Automation execution not found: EX-S10-MISSING"
            )
        else:
            raise AssertionError(
                "Expected ValueError for missing execution"
            )

    finally:
        server.automation_execution_history_service = (
            original_history_service
        )


def test_list_automation_executions_tool():
    history_service = Mock()

    history_service.list.return_value = [
        AutomationExecutionResult(
            execution_id="EX-S10-LIST-002",
            automation_artifact_id="GA002",
            automation_case_id="AC001",
            status="FAILED",
            exit_code=1,
            stdout="",
            stderr="assertion failed",
            duration_seconds=2.0,
            error=None,
        ),
        AutomationExecutionResult(
            execution_id="EX-S10-LIST-001",
            automation_artifact_id="GA001",
            automation_case_id="AC001",
            status="PASSED",
            exit_code=0,
            stdout="1 passed",
            stderr="",
            duration_seconds=1.0,
            error=None,
        ),
    ]

    original_history_service = (
        server.automation_execution_history_service
    )

    server.automation_execution_history_service = (
        history_service
    )

    try:
        result = server.list_automation_executions(
            automation_case_id="AC001",
            limit=10,
        )

        assert [
            item["execution_id"]
            for item in result
        ] == [
            "EX-S10-LIST-002",
            "EX-S10-LIST-001",
        ]

        assert result[0]["status"] == "FAILED"
        assert result[1]["status"] == "PASSED"

        history_service.list.assert_called_once_with(
            automation_case_id="AC001",
            limit=10,
        )

    finally:
        server.automation_execution_history_service = (
            original_history_service
        )



def test_get_automation_execution_report_tool():
    reporting_service = Mock()

    from qa_mcp.models.execution_reporting import (
        AutomationExecutionReport,
    )

    reporting_service.report.return_value = (
        AutomationExecutionReport(
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
    )

    original_service = (
        server.automation_execution_reporting_service
    )

    server.automation_execution_reporting_service = (
        reporting_service
    )

    try:
        result = server.get_automation_execution_report(
            automation_case_id="AC001"
        )

        assert result["total_executions"] == 4
        assert result["passed"] == 2
        assert result["failed"] == 1
        assert result["not_executed"] == 1
        assert result["error"] == 0
        assert result["pass_rate_percent"] == 50.0
        assert result["total_duration_seconds"] == 10.0
        assert result["average_duration_seconds"] == 2.5
        assert result["latest_execution_id"] == "EX004"
        assert result["latest_status"] == "NOT_EXECUTED"

        reporting_service.report.assert_called_once_with(
            automation_case_id="AC001"
        )

    finally:
        server.automation_execution_reporting_service = (
            original_service
        )


def test_get_automation_execution_report_tool_without_filter():
    reporting_service = Mock()

    from qa_mcp.models.execution_reporting import (
        AutomationExecutionReport,
    )

    reporting_service.report.return_value = (
        AutomationExecutionReport(
            total_executions=0,
            passed=0,
            failed=0,
            not_executed=0,
            error=0,
            pass_rate_percent=0.0,
            total_duration_seconds=0.0,
            average_duration_seconds=0.0,
            latest_execution_id=None,
            latest_status=None,
        )
    )

    original_service = (
        server.automation_execution_reporting_service
    )

    server.automation_execution_reporting_service = (
        reporting_service
    )

    try:
        result = server.get_automation_execution_report()

        assert result["total_executions"] == 0
        assert result["pass_rate_percent"] == 0.0
        assert result["latest_execution_id"] is None

        reporting_service.report.assert_called_once_with(
            automation_case_id=None
        )

    finally:
        server.automation_execution_reporting_service = (
            original_service
        )


def test_analyze_automation_failures_tool():
    from unittest.mock import Mock

    from qa_mcp.models.execution_failure_analysis import (
        AutomationExecutionFailureAnalysis,
    )

    analysis_service = Mock()

    analysis_service.analyze.return_value = (
        AutomationExecutionFailureAnalysis(
            total_executions=5,
            failed_executions=2,
            error_executions=1,
            total_failures=3,
            failure_rate_percent=60.0,
            affected_automation_cases=[
                "AC001",
                "AC002",
            ],
            latest_failure_execution_id="EX005",
            latest_failure_status="FAILED",
            failures=[],
        )
    )

    original_service = (
        server.automation_execution_failure_analysis_service
    )

    server.automation_execution_failure_analysis_service = (
        analysis_service
    )

    try:
        result = server.analyze_automation_failures(
            automation_case_id="AC001",
            limit=10,
        )

        assert result["total_executions"] == 5
        assert result["failed_executions"] == 2
        assert result["error_executions"] == 1
        assert result["total_failures"] == 3
        assert result["failure_rate_percent"] == 60.0
        assert result["affected_automation_cases"] == [
            "AC001",
            "AC002",
        ]
        assert result["latest_failure_execution_id"] == "EX005"
        assert result["latest_failure_status"] == "FAILED"

        analysis_service.analyze.assert_called_once_with(
            automation_case_id="AC001",
            limit=10,
        )

    finally:
        server.automation_execution_failure_analysis_service = (
            original_service
        )


def test_analyze_automation_failures_tool_without_filter():
    from unittest.mock import Mock

    from qa_mcp.models.execution_failure_analysis import (
        AutomationExecutionFailureAnalysis,
    )

    analysis_service = Mock()

    analysis_service.analyze.return_value = (
        AutomationExecutionFailureAnalysis(
            total_executions=0,
            failed_executions=0,
            error_executions=0,
            total_failures=0,
            failure_rate_percent=0.0,
            affected_automation_cases=[],
            failures=[],
        )
    )

    original_service = (
        server.automation_execution_failure_analysis_service
    )

    server.automation_execution_failure_analysis_service = (
        analysis_service
    )

    try:
        result = server.analyze_automation_failures()

        assert result["total_failures"] == 0
        assert result["failure_rate_percent"] == 0.0

        analysis_service.analyze.assert_called_once_with(
            automation_case_id=None,
            limit=50,
        )

    finally:
        server.automation_execution_failure_analysis_service = (
            original_service
        )
