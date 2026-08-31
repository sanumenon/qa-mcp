from qa_mcp.core.automation.code_generation_service import (
    AutomationCodeGenerationService,
)
from qa_mcp.core.automation.execution_service import (
    AutomationExecutionService,
)
from qa_mcp.models.schemas import AutomationCase


def test_generated_playwright_artifact_executes_in_real_browser():
    automation_case = AutomationCase(
        id="AC-S9.3-001",
        test_case_id="TC-S9.3-001",
        title="Validate login form interaction",
        automation_type="UI",
        framework="Playwright",
        priority="High",
        confidence="High",
        steps=[
            "goto: data:text/html,<html><body>"
            "<input id='username'>"
            "<button id='login'>Login</button>"
            "<div id='result' style='display:none'>Login successful</div>"
            "<script>"
            "document.querySelector('#login').onclick="
            "function(){document.querySelector('#result').style.display='block'}"
            "</script>"
            "</body></html>",
            "fill: #username = test-user",
            "click: #login",
        ],
        assertions=[
            "visible: #username",
        ],
        limitations=[],
    )

    generator = AutomationCodeGenerationService()
    artifact = generator.generate(automation_case)

    assert artifact.framework == "Playwright"
    assert artifact.language == "Python"
    assert artifact.code

    executor = AutomationExecutionService()
    result = executor.execute(artifact)

    assert result.status == "PASSED", (
        f"Real Playwright execution failed.\n"
        f"exit_code={result.exit_code}\n"
        f"stdout={result.stdout}\n"
        f"stderr={result.stderr}\n"
        f"error={result.error}"
    )

    assert result.exit_code == 0
    assert result.error is None


def test_real_playwright_assertion_failure_returns_failed():
    automation_case = AutomationCase(
        id="AC-S9.3-002",
        test_case_id="TC-S9.3-002",
        title="Validate failed browser assertion",
        automation_type="UI",
        framework="Playwright",
        priority="High",
        confidence="High",
        steps=[
            "goto: data:text/html,<html><body>"
            "<div id='message'>Actual value</div>"
            "</body></html>",
        ],
        assertions=[
            "text: #message = Expected value",
        ],
        limitations=[],
    )

    generator = AutomationCodeGenerationService()
    artifact = generator.generate(automation_case)

    executor = AutomationExecutionService()
    result = executor.execute(artifact)

    assert result.status == "FAILED"
    assert result.exit_code != 0
    assert result.error is None


def test_real_playwright_invalid_browser_artifact_returns_failed():
    automation_case = AutomationCase(
        id="AC-S9.3-003",
        test_case_id="TC-S9.3-003",
        title="Validate malformed generated browser code",
        automation_type="UI",
        framework="Playwright",
        priority="High",
        confidence="High",
        steps=[
            "goto: data:text/html,<html><body>Valid page</body></html>",
        ],
        assertions=[
            "visible: body",
        ],
        limitations=[],
    )

    generator = AutomationCodeGenerationService()
    artifact = generator.generate(automation_case)

    # Deliberately corrupt the generated artifact after generation.
    artifact.code = artifact.code + "\nthis is invalid python syntax !!!"

    executor = AutomationExecutionService()
    result = executor.execute(artifact)

    assert result.status == "FAILED"
    assert result.exit_code != 0
