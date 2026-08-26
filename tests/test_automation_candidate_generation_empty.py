from unittest.mock import Mock

from qa_mcp.core.automation.candidate_generation_service import (
    AutomationCandidateGenerationService,
)
from qa_mcp.models.schemas import (
    AutomationCandidateResult,
    TestCase,
)


def test_candidate_generation_service_skips_generation_when_no_candidates():

    candidate_service = Mock()

    candidate_service.select_candidates.return_value = (
        AutomationCandidateResult(
            candidate_ids=[],
            manual_ids=[
                "TC001",
            ],
            total=1,
        )
    )

    automation_service = Mock()

    service = AutomationCandidateGenerationService(
        candidate_service=candidate_service,
        automation_service=automation_service,
    )

    test_cases = [
        TestCase(
            id="TC001",
            title="Exploratory testing",
            test_type="Exploratory",
            priority="High",
            preconditions=[],
            steps=[
                "Explore application",
            ],
            expected_result="Issues identified",
        )
    ]

    result = service.generate(
        test_cases
    )

    assert result == []

    automation_service.generate_automation.assert_not_called()