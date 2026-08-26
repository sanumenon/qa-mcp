from qa_mcp.models.schemas import TestCase

from qa_mcp.core.automation.candidate_selector import (
    AutomationCandidateSelector,
)


def test_selects_automation_candidates():

    selector = AutomationCandidateSelector()

    test_cases = [
        TestCase(
            id="TC001",
            title="Successful login",
            test_type="Functional",
            priority="High",
            preconditions=[
                "User account exists",
            ],
            steps=[
                "Open login page",
                "Enter valid username",
                "Enter valid password",
                "Click Login",
            ],
            expected_result="Dashboard is displayed",
        ),
        TestCase(
            id="TC002",
            title="Verify login error",
            test_type="Functional",
            priority="Medium",
            preconditions=[],
            steps=[
                "Open login page",
                "Enter invalid password",
                "Click Login",
            ],
            expected_result="Error message is displayed",
        ),
        TestCase(
            id="TC003",
            title="Exploratory login testing",
            test_type="Exploratory",
            priority="High",
            preconditions=[],
            steps=[
                "Explore login behavior",
            ],
            expected_result="Unexpected issues are identified",
        ),
    ]

    result = selector.select_candidates(
        test_cases
    )

    assert result == [
        "TC001",
        "TC002",
    ]

def test_rejects_functional_test_without_steps():

    selector = AutomationCandidateSelector()

    test_cases = [
        TestCase(
            id="TC004",
            title="Incomplete functional test",
            test_type="Functional",
            priority="High",
            preconditions=[],
            steps=[],
            expected_result="Dashboard is displayed",
        )
    ]

    result = selector.select_candidates(
        test_cases
    )

    assert result == []

def test_rejects_functional_test_without_expected_result():

    selector = AutomationCandidateSelector()

    test_cases = [
        TestCase(
            id="TC005",
            title="Incomplete expected result",
            test_type="Functional",
            priority="High",
            preconditions=[],
            steps=[
                "Open login page",
                "Enter username",
            ],
            expected_result="",
        )
    ]

    result = selector.select_candidates(
        test_cases
    )

    assert result == []

def test_rejects_low_priority_functional_test():

    selector = AutomationCandidateSelector()

    test_cases = [
        TestCase(
            id="TC006",
            title="Low priority functional test",
            test_type="Functional",
            priority="Low",
            preconditions=[],
            steps=[
                "Open login page",
                "Enter username",
                "Enter password",
            ],
            expected_result="Dashboard is displayed",
        )
    ]

    result = selector.select_candidates(
        test_cases
    )

    assert result == []