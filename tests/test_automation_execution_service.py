import pytest

from qa_mcp.core.automation.execution_service import (
    AutomationExecutionService,
)
from qa_mcp.models.schemas import (
    GeneratedAutomationArtifact,
)


def build_artifact(**overrides):
    data = {
        "id": "GA001",
        "automation_case_id": "AC001",
        "framework": "Playwright",
        "language": "Python",
        "file_name": "test_successful_login.py",
        "code": (
            "def test_successful_login(page):\n"
            "    pass"
        ),
    }

    data.update(overrides)

    return GeneratedAutomationArtifact(**data)


def test_execution_returns_not_executed_foundation_result():

    service = AutomationExecutionService()

    result = service.execute(
        build_artifact()
    )

    assert result.automation_artifact_id == "GA001"
    assert result.execution_id == "EX001"
    assert result.status == "NOT_EXECUTED"
    assert result.exit_code is None
    assert result.stdout == ""
    assert result.stderr == ""
    assert result.error is None


def test_empty_code_fails_execution():

    service = AutomationExecutionService()

    with pytest.raises(
        ValueError,
        match="Automation artifact must contain code",
    ):
        service.execute(
            build_artifact(code="")
        )


def test_missing_framework_fails_execution():

    service = AutomationExecutionService()

    with pytest.raises(
        ValueError,
        match="Automation artifact must specify a framework",
    ):
        service.execute(
            build_artifact(framework="")
        )


def test_unsupported_framework_fails_execution():

    service = AutomationExecutionService()

    with pytest.raises(
        ValueError,
        match="Unsupported automation framework",
    ):
        service.execute(
            build_artifact(
                framework="Cypress"
            )
        )
