from unittest.mock import Mock

from qa_mcp.core.automation.service import (
    AutomationService,
)
from qa_mcp.models.schemas import (
    AutomationCase,
    AutomationCaseResponse,
    TestCase as QATestCase,
)


def test_automation_service_requires_generator():

    generator = Mock()

    service = AutomationService(
        generator
    )

    assert service.generator is generator


def test_generate_automation_delegates_to_generator():

    generator = Mock()

    expected = AutomationCaseResponse(
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

    generator.generate.return_value = expected

    service = AutomationService(
        generator
    )

    test_case = QATestCase(
        id="TC001",
        title="Successful login",
        test_type="Functional",
        priority="High",
        preconditions=[],
        steps=[
            "Open login page",
        ],
        expected_result="Dashboard is displayed",
    )

    result = service.generate_automation(
        test_case
    )

    generator.generate.assert_called_once_with(
        test_case
    )

    assert result is expected