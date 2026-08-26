from qa_mcp.core.automation.candidate_selector import (
    AutomationCandidateSelector,
)
from qa_mcp.core.automation.candidate_service import (
    AutomationCandidateService,
)
from qa_mcp.models.schemas import (
    QASuiteResult,
    RequirementAnalysis,
    RequirementRequest,
    TestCase,
    TestCaseResponse,
    TestCaseReview,
)


def test_qa_suite_result_can_be_processed_for_automation_candidates():

    suite_result = QASuiteResult(
        requirement=RequirementRequest(
            requirement_id="REQ001",
            requirement="User should be able to login",
            application="QA MCP",
            environment="test",
        ),
        analysis=RequirementAnalysis(
            summary="Login requirement analysis",
            actors=[],
            functional_requirements=[
                "User can login",
            ],
            business_rules=[],
            preconditions=[],
            main_workflows=[
                "User logs in",
            ],
            positive_scenarios=[
                "Valid user logs in",
            ],
            negative_scenarios=[],
            edge_cases=[],
            missing_information=[],
            recommended_test_types=[
                "Functional",
            ],
        ),
        test_cases=TestCaseResponse(
            test_cases=[
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
        ),
        review=TestCaseReview(
            overall_quality="Good",
            coverage_score=90,
            duplicate_test_cases=[],
            missing_scenarios=[],
            weak_test_cases=[],
            requirement_gaps=[],
            priority_issues=[],
            recommendations=[],
            summary="Good coverage",
        ),
    )

    service = AutomationCandidateService(
        AutomationCandidateSelector()
    )

    result = service.select_candidates(
        suite_result.test_cases.test_cases
    )

    assert result.total == 2

    assert result.candidate_ids == [
        "TC001",
    ]

    assert result.manual_ids == [
        "TC002",
    ]