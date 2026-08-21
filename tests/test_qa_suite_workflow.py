import json

from qa_mcp.models.schemas import (
    RequirementRequest,
)

from qa_mcp.tools.workflow.qa_suite import (
    QASuiteWorkflow,
)


class WorkflowLLM:

    def __init__(self):

        self.calls: list[str] = []

    def generate(
        self,
        prompt: str,
    ) -> str:

        self.calls.append(
            prompt
        )

        # Requirement Analyzer
        if (
            "Analyze the requirement"
            in prompt
        ):

            return json.dumps({

                "summary": (
                    "User can reset a password "
                    "using email."
                ),

                "actors": [
                    "Registered User"
                ],

                "functional_requirements": [
                    "User can request a "
                    "password reset."
                ],

                "business_rules": [],

                "preconditions": [
                    "User has a registered account."
                ],

                "main_workflows": [
                    "Request password reset"
                ],

                "positive_scenarios": [
                    "Registered email receives "
                    "reset instructions."
                ],

                "negative_scenarios": [
                    "Unregistered email is submitted."
                ],

                "edge_cases": [
                    "Expired reset link"
                ],

                "missing_information": [
                    "Reset link expiry duration"
                ],

                "recommended_test_types": [
                    "functional",
                    "negative",
                    "boundary",
                ],
            })

        # Test Case Generator
        if (
            "Generate comprehensive, independent "
            "test cases"
            in prompt
        ):

            return json.dumps({

                "test_cases": [

                    {
                        "id": "TC001",

                        "title": (
                            "Reset password "
                            "with registered email"
                        ),

                        "priority": "High",

                        "test_type": "Functional",

                        "preconditions": [
                            "User has a "
                            "registered account."
                        ],

                        "steps": [
                            "Open the login page.",
                            "Select Forgot Password.",
                            "Enter the registered email.",
                            "Submit the request.",
                        ],

                        "expected_result": (
                            "Password reset "
                            "instructions are sent."
                        ),
                    }
                ]
            })

        # Test Case Reviewer
        if (
            "Review the suite for completeness "
            "and quality"
            in prompt
        ):

            return json.dumps({

                "overall_quality": "Good",

                "coverage_score": 80,

                "duplicate_test_cases": [],

                "missing_scenarios": [
                    "Unregistered email"
                ],

                "weak_test_cases": [],

                "requirement_gaps": [],

                "priority_issues": [],

                "recommendations": [
                    "Add an unregistered "
                    "email scenario."
                ],

                "summary": (
                    "Good baseline coverage."
                ),
            })

        raise AssertionError(
            "Unexpected workflow prompt."
        )


def test_complete_qa_suite_workflow():

    llm = WorkflowLLM()

    workflow = QASuiteWorkflow(
        llm
    )

    result = workflow.run(

        RequirementRequest(

            requirement=(
                "User can reset password "
                "using email."
            ),

            application="Customer Portal",
        )
    )

    assert (
        result.requirement.application
        == "Customer Portal"
    )

    assert (
        result.analysis.summary.startswith(
            "User can reset"
        )
    )

    assert (
        result.test_cases.test_cases[0].id
        == "TC001"
    )

    assert (
        result.review.coverage_score
        == 80
    )

    assert len(
        llm.calls
    ) == 3


def test_workflow_executes_three_stages():

    llm = WorkflowLLM()

    workflow = QASuiteWorkflow(
        llm
    )

    workflow.run(

        RequirementRequest(

            requirement=(
                "User can reset password."
            ),

            application="Customer Portal",
        )
    )

    assert (
        "Analyze the requirement"
        in llm.calls[0]
    )

    assert (
        "Generate comprehensive"
        in llm.calls[1]
    )

    assert (
        "Review the suite"
        in llm.calls[2]
    )