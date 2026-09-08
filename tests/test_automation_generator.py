import json
from qa_mcp.models.schemas import (
    AutomationCase,
    AutomationCaseResponse,
)


def test_automation_case_schema():

    automation_case = AutomationCase(
        id="AC001",
        test_case_id="TC001",
        title="Automate successful login",
        automation_type="UI",
        framework="Playwright",
        priority="High",
        confidence="High",
        preconditions=[
            "User account exists",
        ],
        test_data=[
            {
                "field": "username",
                "value": "user@example.com",
            },
            {
                "field": "password",
                "value": "ValidPassword123",
            },
        ],
        steps=[
            "Open login page",
            "Enter valid username",
            "Enter valid password",
            "Click Login",
        ],
        assertions=[
            "User is redirected to dashboard",
        ],
        limitations=[],
    )

    assert automation_case.id == "AC001"
    assert automation_case.test_case_id == "TC001"
    assert automation_case.automation_type == "UI"
    assert automation_case.framework == "Playwright"
    assert automation_case.confidence == "High"


def test_automation_case_response_schema():

    response = AutomationCaseResponse(
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

    assert len(response.automation_cases) == 1
    assert response.automation_cases[0].id == "AC001"



def test_automation_case_generator_requires_normalized_steps():
    from qa_mcp.tools.automation.generator import AutomationCaseGenerator
    from qa_mcp.models.schemas import TestCase

    class FakeLLM:
        def generate(self, prompt):
            assert "goto: URL" in prompt
            assert "click: selector" in prompt
            assert "fill: selector = value" in prompt
            assert "press: selector = key" in prompt
            assert "Do not use natural-language navigation" in prompt

            return json.dumps({
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
                        "test_data": [],
                        "steps": [
                            "goto: http://localhost:8000/reset-password",
                            "fill: #email = user@example.com",
                            "click: #submit",
                        ],
                        "assertions": [
                            "visible: #confirmation",
                        ],
                        "limitations": [],
                    }
                ]
            })

    generator = AutomationCaseGenerator(FakeLLM())

    result = generator.generate(
        TestCase(
            id="TC001",
            title="Reset password",
            priority="High",
            test_type="Functional",
            preconditions=[],
            steps=["Reset password using email"],
            expected_result="Password reset confirmation is displayed",
        )
    )

    assert result.automation_cases[0].steps[0].startswith("goto: ")
