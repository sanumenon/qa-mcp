from unittest.mock import Mock

from qa_mcp import server
from qa_mcp.models.schemas import (
    AutomationCase,
)


def test_generate_automation_for_candidates_tool():

    mock_service = Mock()

    mock_service.generate.return_value = [
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

    original_service = (
        server.automation_candidate_generation_service
    )

    server.automation_candidate_generation_service = (
        mock_service
    )

    try:
        result = (
            server.generate_automation_for_candidates(
                test_cases=[
                    {
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
                ]
            )
        )

        assert result == [
            {
                "id": "AC001",
                "test_case_id": "TC001",
                "title": "Automate successful login",
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
        ]

        mock_service.generate.assert_called_once()

    finally:
        server.automation_candidate_generation_service = (
            original_service
        )