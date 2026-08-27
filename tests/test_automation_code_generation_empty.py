import pytest

from qa_mcp.core.automation.code_generation_service import (
    AutomationCodeGenerationService,
)
from qa_mcp.models.schemas import AutomationCase


def test_code_generation_without_steps_fails():

    automation_case = AutomationCase(
        id="AC002",
        test_case_id="TC002",
        title="Invalid login",
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

    service = AutomationCodeGenerationService()

    with pytest.raises(
        ValueError,
        match="Automation case must contain at least one step",
    ):
        service.generate(automation_case)


def test_code_generation_without_assertions_fails():

    automation_case = AutomationCase(
        id="AC003",
        test_case_id="TC003",
        title="Successful login",
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

    service = AutomationCodeGenerationService()

    with pytest.raises(
        ValueError,
        match="Automation case must contain at least one assertion",
    ):
        service.generate(automation_case)


def test_code_generation_without_framework_fails():

    automation_case = AutomationCase(
        id="AC004",
        test_case_id="TC004",
        title="Successful login",
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

    service = AutomationCodeGenerationService()

    with pytest.raises(
        ValueError,
        match="Automation case must specify a framework",
    ):
        service.generate(automation_case)


def test_code_generation_with_unsupported_framework_fails():

    automation_case = AutomationCase(
        id="AC005",
        test_case_id="TC005",
        title="Successful login",
        automation_type="UI",
        framework="Selenium",
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

    service = AutomationCodeGenerationService()

    with pytest.raises(
        ValueError,
        match="Unsupported automation framework",
    ):
        service.generate(automation_case)
