from qa_mcp.core.automation.validator import (
    AutomationValidator,
)
from qa_mcp.models.schemas import AutomationCase


def test_valid_automation_case_passes_validation():

    automation_case = AutomationCase(
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

    validator = AutomationValidator()

    result = validator.validate(
        automation_case
    )

    assert result.valid is True
    assert result.automation_case_id == "AC001"
    assert result.test_case_id == "TC001"
    assert result.errors == []

def test_automation_case_without_steps_fails_validation():

    automation_case = AutomationCase(
        id="AC002",
        test_case_id="TC002",
        title="Automate invalid login",
        automation_type="UI",
        framework="Playwright",
        priority="High",
        confidence="High",
        preconditions=[],
        test_data=[],
        steps=[],
        assertions=[
            "Error displayed",
        ],
        limitations=[],
    )

    validator = AutomationValidator()

    result = validator.validate(
        automation_case
    )

    assert result.valid is False
    assert result.automation_case_id == "AC002"
    assert result.test_case_id == "TC002"
    assert "Automation case must contain at least one step" in result.errors

def test_automation_case_without_assertions_fails_validation():

    automation_case = AutomationCase(
        id="AC003",
        test_case_id="TC003",
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
        assertions=[],
        limitations=[],
    )

    validator = AutomationValidator()

    result = validator.validate(
        automation_case
    )

    assert result.valid is False
    assert result.automation_case_id == "AC003"
    assert result.test_case_id == "TC003"
    assert "Automation case must contain at least one assertion" in result.errors

def test_automation_case_without_framework_fails_validation():

    automation_case = AutomationCase(
        id="AC004",
        test_case_id="TC004",
        title="Automate successful login",
        automation_type="UI",
        framework="",
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

    validator = AutomationValidator()

    result = validator.validate(
        automation_case
    )

    assert result.valid is False
    assert result.automation_case_id == "AC004"
    assert result.test_case_id == "TC004"
    assert "Automation case must specify a framework" in result.errors