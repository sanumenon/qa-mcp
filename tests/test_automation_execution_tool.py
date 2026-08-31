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
