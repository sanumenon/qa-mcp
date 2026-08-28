from qa_mcp.core.automation.code_generation_service import (
    AutomationCodeGenerationService,
)
from qa_mcp.models.schemas import AutomationCase

def test_code_generation_service_generates_playwright_python_artifact():

    automation_case = AutomationCase(
        id="AC001",
        test_case_id="TC001",
        title="Successful login",
        automation_type="UI",
        framework="Playwright",
        priority="High",
        confidence="High",
        preconditions=[],
        test_data=[],
        steps=[
            "goto: http://localhost:8000/login",
            "fill: #username = testuser",
            "fill: #password = secret",
            "click: #login",
        ],
        assertions=[
            "visible: #dashboard",
        ],
        limitations=[],
    )

    service = AutomationCodeGenerationService()

    result = service.generate(automation_case)

    assert result.id == "GA001"
    assert result.automation_case_id == "AC001"
    assert result.framework == "Playwright"
    assert result.language == "Python"
    assert result.file_name == "test_successful_login.py"

    assert (
        "page.goto('http://localhost:8000/login')"
        in result.code
    )

    assert (
        "page.locator('#username').fill('testuser')"
        in result.code
    )

    assert (
        "page.locator('#password').fill('secret')"
        in result.code
    )

    assert (
        "page.locator('#login').click()"
        in result.code
    )

    assert (
        "expect(page.locator('#dashboard')).to_be_visible()"
        in result.code
    )