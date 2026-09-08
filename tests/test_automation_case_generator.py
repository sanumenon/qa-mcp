from qa_mcp.models.schemas import (
    TestCase as QATestCase,
    AutomationCaseResponse,
)

from qa_mcp.tools.automation.generator import (
    AutomationCaseGenerator,
)


class MockLLM:

    def generate(self, prompt: str) -> str:
        return """
        {
            "automation_cases": [
                {
                    "id": "AC001",
                    "test_case_id": "TC001",
                    "title": "Automate successful login",
                    "automation_type": "UI",
                    "framework": "Playwright",
                    "priority": "High",
                    "confidence": "High",
                    "preconditions": [
                        "User account exists"
                    ],
                    "test_data": [
                        {
                            "field": "username",
                            "value": "user@example.com"
                        },
                        {
                            "field": "password",
                            "value": "ValidPassword123"
                        }
                    ],
                    "steps": [
                        "Open login page",
                        "Enter valid username",
                        "Enter valid password",
                        "Click Login"
                    ],
                    "assertions": [
                        "User is redirected to dashboard"
                    ],
                    "limitations": []
                }
            ]
        }
        """


def test_automation_case_generator_returns_response():

    llm = MockLLM()

    generator = AutomationCaseGenerator(llm)

    test_case = QATestCase(
    id="TC001",
    title="Successful login",
    test_type="Functional",
    priority="High",
    preconditions=[
        "User account exists"
    ],
    steps=[
        "Open login page",
        "Enter valid username",
        "Enter valid password",
        "Click Login",
    ],
    expected_result="User is redirected to dashboard",
)

    result = generator.generate(
        test_case
    )

    assert isinstance(
        result,
        AutomationCaseResponse,
    )

    assert len(
        result.automation_cases
    ) == 1

    automation_case = (
        result.automation_cases[0]
    )

    assert (
        automation_case.test_case_id
        == "TC001"
    )

    assert (
        automation_case.framework
        == "Playwright"
    )

class MockStructuredAutomationLLM:

    def generate(self, prompt: str) -> str:
        return """
        {
            "automation_cases": [
                {
                    "id": "AC001",
                    "test_case_id": "TC001",
                    "title": "Automate password reset",
                    "automation_type": "UI",
                    "framework": "Playwright",
                    "priority": "High",
                    "confidence": "High",
                    "preconditions": [],
                    "test_data": [
                        {
                            "name": "email",
                            "value": "user@example.com",
                            "description": "Registered email address"
                        }
                    ],
                    "steps": [
                        "goto: http://localhost:8000/reset-password",
                        "fill: #email = user@example.com",
                        "click: #submit",
                        "# Extract reset token from email using email API or test mailbox"
                    ],
                    "assertions": [
                        {
                            "type": "element_visible",
                            "selector": "#confirmation",
                            "description": "Confirmation is visible"
                        }
                    ],
                    "limitations": []
                }
            ]
        }
        """


def test_automation_case_generator_normalizes_structured_automation_payload():

    generator = AutomationCaseGenerator(
        MockStructuredAutomationLLM()
    )

    test_case = QATestCase(
        id="TC001",
        title="Reset password",
        test_type="Functional",
        priority="High",
        preconditions=[],
        steps=[
            "Reset password using email"
        ],
        expected_result=(
            "Password reset confirmation is displayed"
        ),
    )

    result = generator.generate(test_case)

    automation_case = result.automation_cases[0]

    assert len(automation_case.test_data) == 1
    assert automation_case.test_data[0].field == "email"
    assert automation_case.test_data[0].value == "user@example.com"

    assert automation_case.steps == [
        "goto: http://localhost:8000/reset-password",
        "fill: #email = user@example.com",
        "click: #submit",
    ]

    assert (
        "# Extract reset token from email using email API or test mailbox"
        in automation_case.limitations
    )

    assert automation_case.assertions == [
        "visible: #confirmation"
    ]
