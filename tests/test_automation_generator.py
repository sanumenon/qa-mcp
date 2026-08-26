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
            "Valid username",
            "Valid password",
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

