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