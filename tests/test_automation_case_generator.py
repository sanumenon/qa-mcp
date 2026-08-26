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
                        "Valid username",
                        "Valid password"
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