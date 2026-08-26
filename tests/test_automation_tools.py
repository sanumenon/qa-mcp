from unittest.mock import Mock

from qa_mcp.models.schemas import (
    AutomationCase,
    AutomationCaseResponse,
)

from qa_mcp.models.schemas import (
    TestCase as QATestCase,
)


def test_generate_automation_tool():

    from qa_mcp import server

    mock_service = Mock()

    mock_service.generate_automation.return_value = (
        AutomationCaseResponse(
            automation_cases=[
                AutomationCase(
                    id="AC001",
                    test_case_id="TC001",
                    title="Automate successful login",
                    automation_type="UI",
                    framework="Playwright",
                    priority="High",
                    confidence="High",
                    preconditions=[],
                    test_data=[],
                    steps=[
                        "Open login page",
                    ],
                    assertions=[
                        "Dashboard is displayed",
                    ],
                    limitations=[],
                )
            ]
        )
    )

    original_service = server.automation_service

    server.automation_service = mock_service

    try:
        result = server.generate_automation(
            test_case={
                "id": "TC001",
                "title": "Successful login",
                "test_type": "Functional",
                "priority": "High",
                "preconditions": [],
                "steps": [
                    "Open login page",
                ],
                "expected_result": (
                    "Dashboard is displayed"
                ),
            }
        )

        mock_service.generate_automation.assert_called_once()

        assert (
            result["automation_cases"][0]["id"]
            == "AC001"
        )

    finally:
        server.automation_service = (
            original_service
        )