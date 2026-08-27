from unittest.mock import Mock

from qa_mcp import server
from qa_mcp.models.schemas import GeneratedAutomationArtifact


def test_generate_automation_code_tool():

    mock_service = Mock()

    mock_service.generate.return_value = (
        GeneratedAutomationArtifact(
            id="GA001",
            automation_case_id="AC001",
            framework="Playwright",
            language="Python",
            file_name="test_successful_login.py",
            code=(
                "def test_successful_login(page):\n"
                "    pass"
            ),
        )
    )

    original_service = (
        server.automation_code_generation_service
    )

    server.automation_code_generation_service = (
        mock_service
    )

    try:
        result = server.generate_automation_code(
            automation_case={
                "id": "AC001",
                "test_case_id": "TC001",
                "title": "Successful login",
                "automation_type": "UI",
                "framework": "Playwright",
                "priority": "High",
                "confidence": "High",
                "preconditions": [],
                "test_data": [],
                "steps": [
                    "Open login page",
                ],
                "assertions": [
                    "Dashboard is displayed",
                ],
                "limitations": [],
            }
        )

        assert result["id"] == "GA001"
        assert result["automation_case_id"] == "AC001"
        assert result["framework"] == "Playwright"
        assert result["language"] == "Python"
        assert result["file_name"] == "test_successful_login.py"
        assert "def test_successful_login" in result["code"]

        mock_service.generate.assert_called_once()

    finally:
        server.automation_code_generation_service = (
            original_service
        )
