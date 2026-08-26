from unittest.mock import Mock

from qa_mcp.models.schemas import (
    AutomationCandidateResult,
)

from qa_mcp import server


def test_select_automation_candidates_tool():

    mock_service = Mock()

    mock_service.select_candidates.return_value = (
        AutomationCandidateResult(
            candidate_ids=[
                "TC001",
                "TC002",
            ],
            manual_ids=[
                "TC003",
            ],
            total=3,
        )
    )

    original_service = (
        server.automation_candidate_service
    )

    server.automation_candidate_service = (
        mock_service
    )

    try:
        result = (
            server.select_automation_candidates(
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
                    },
                    {
                        "id": "TC002",
                        "title": "Invalid login",
                        "test_type": "Functional",
                        "priority": "Medium",
                        "preconditions": [],
                        "steps": [
                            "Open login page",
                        ],
                        "expected_result": (
                            "Error displayed"
                        ),
                    },
                    {
                        "id": "TC003",
                        "title": "Exploratory testing",
                        "test_type": "Exploratory",
                        "priority": "High",
                        "preconditions": [],
                        "steps": [
                            "Explore application",
                        ],
                        "expected_result": (
                            "Issues identified"
                        ),
                    },
                ]
            )
        )

        assert result == {
            "candidate_ids": [
                "TC001",
                "TC002",
            ],
            "manual_ids": [
                "TC003",
            ],
            "total": 3,
        }

        mock_service.select_candidates.assert_called_once()

    finally:
        server.automation_candidate_service = (
            original_service
        )