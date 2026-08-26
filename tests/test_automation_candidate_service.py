from qa_mcp.models.schemas import (
    AutomationCandidateResult,
    TestCase,
)

from qa_mcp.core.automation.candidate_service import (
    AutomationCandidateService,
)


def test_candidate_service_returns_structured_result():

    class FakeSelector:

        def select_candidates(
            self,
            test_cases,
        ):
            return [
                "TC001",
                "TC002",
            ]

    service = AutomationCandidateService(
        FakeSelector()
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
            title="Invalid login",
            test_type="Functional",
            priority="Medium",
            preconditions=[],
            steps=[
                "Open login page",
            ],
            expected_result="Error displayed",
        ),
        TestCase(
            id="TC003",
            title="Exploratory testing",
            test_type="Exploratory",
            priority="High",
            preconditions=[],
            steps=[
                "Explore application",
            ],
            expected_result="Issues identified",
        ),
    ]

    result = service.select_candidates(
        test_cases
    )

    assert isinstance(
        result,
        AutomationCandidateResult,
    )

    assert result.candidate_ids == [
        "TC001",
        "TC002",
    ]

    assert result.manual_ids == [
        "TC003",
    ]

    assert result.total == 3