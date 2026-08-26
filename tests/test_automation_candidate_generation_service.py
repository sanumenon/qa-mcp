from unittest.mock import Mock

from qa_mcp.core.automation.candidate_generation_service import (
    AutomationCandidateGenerationService,
)
from qa_mcp.models.schemas import (
    AutomationCase,
    AutomationCandidateResult,
    TestCase,
)


def test_candidate_generation_service_generates_only_selected_cases():

    candidate_service = Mock()

    candidate_service.select_candidates.return_value = (
        AutomationCandidateResult(
            candidate_ids=[
                "TC001",
            ],
            manual_ids=[
                "TC002",
            ],
            total=2,
        )
    )

    automation_service = Mock()

    automation_service.generate_automation.return_value = (
        {
            "test_case_id": "TC001",
        }
    )

    service = AutomationCandidateGenerationService(
        candidate_service=candidate_service,
        automation_service=automation_service,
    )

    test_cases = [
        TestCase(
            id="TC001",
            title="Successful login",
            test_type="Functional",
            priority="High",
            preconditions=[],
            steps=[
                "Open login page",
            ],
            expected_result="Dashboard is displayed",
        ),
        TestCase(
            id="TC002",
            title="Exploratory login",
            test_type="Exploratory",
            priority="High",
            preconditions=[],
            steps=[
                "Explore login behavior",
            ],
            expected_result="Issues identified",
        ),
    ]

    result = service.generate(
        test_cases
    )

    candidate_service.select_candidates.assert_called_once_with(
        test_cases
    )

    automation_service.generate_automation.assert_called_once_with(
        test_cases[0]
    )

    assert result == [
        {
            "test_case_id": "TC001",
        }
    ]