import json

import pytest

from qa_mcp.models.schemas import (
    RequirementAnalysis,
    RequirementRequest,
    TestCaseResponse as TestCases,
)

from qa_mcp.tools.testcase.reviewer import (
    TestCaseReviewer as Reviewer,
)


class FakeLLM:

    def __init__(self, payload: dict):
        self.payload = payload
        self.last_prompt: str = ""

    def generate(
        self,
        prompt: str,
    ) -> str:

        self.last_prompt = prompt

        return json.dumps(
            self.payload
        )


def sample_analysis():

    return RequirementAnalysis(

        summary=(
            "User can reset a password "
            "using registered email."
        ),

        actors=[
            "Registered User"
        ],

        functional_requirements=[
            "User can request a password reset."
        ],

        business_rules=[],

        preconditions=[
            "User has a registered account."
        ],

        main_workflows=[
            "Request password reset"
        ],

        positive_scenarios=[
            "Registered email receives "
            "reset instructions."
        ],

        negative_scenarios=[
            "Unregistered email is submitted."
        ],

        edge_cases=[
            "Expired reset link"
        ],

        missing_information=[
            "Reset link expiry duration"
        ],

        recommended_test_types=[
            "functional",
            "negative",
            "boundary",
        ],
    )


def sample_test_cases():

    return TestCases.model_validate({

        "test_cases": [

            {
                "id": "TC001",

                "title": (
                    "Reset password with "
                    "registered email"
                ),

                "priority": "High",

                "test_type": "Functional",

                "preconditions": [
                    "User has a registered account."
                ],

                "steps": [
                    "Open the login page.",
                    "Select Forgot Password.",
                    "Enter the registered email.",
                    "Submit the request.",
                ],

                "expected_result": (
                    "Password reset instructions "
                    "are sent."
                ),
            },

            {
                "id": "TC002",

                "title": (
                    "Reset password with "
                    "unregistered email"
                ),

                "priority": "High",

                "test_type": "Negative",

                "preconditions": [],

                "steps": [
                    "Open the login page.",
                    "Select Forgot Password.",
                    "Enter an unregistered email.",
                    "Submit the request.",
                ],

                "expected_result": (
                    "The application handles the "
                    "request according to the "
                    "defined policy."
                ),
            },
        ]
    })


def sample_review():

    return {

        "overall_quality": "Good",

        "coverage_score": 85,

        "duplicate_test_cases": [],

        "missing_scenarios": [
            "Expired reset link"
        ],

        "weak_test_cases": [],

        "requirement_gaps": [],

        "priority_issues": [],

        "recommendations": [
            "Add an explicit expired-link scenario."
        ],

        "summary": (
            "Good baseline coverage with "
            "one edge case missing."
        ),
    }


def test_reviewer_returns_structured_review():

    fake_llm = FakeLLM(
        sample_review()
    )

    reviewer = Reviewer(
        fake_llm
    )

    result = reviewer.review(

        requirement=RequirementRequest(
            requirement=(
                "User can reset password "
                "using email."
            ),
            application="Customer Portal",
        ),

        analysis=sample_analysis(),

        test_cases=sample_test_cases(),
    )

    assert (
        result.overall_quality == "Good"
    )

    assert (
        result.coverage_score == 85
    )

    assert (
        "Expired reset link"
        in result.missing_scenarios
    )

    assert (
        "Customer Portal"
        in fake_llm.last_prompt
    )

    assert (
        "TC001"
        in fake_llm.last_prompt
    )


def test_reviewer_rejects_invalid_json():

    class InvalidLLM:

        def generate(
            self,
            prompt: str,
        ) -> str:

            return "not-json"

    reviewer = Reviewer(
        InvalidLLM()
    )

    with pytest.raises(
        ValueError,
        match="invalid JSON",
    ):

        reviewer.review(

            requirement=RequirementRequest(
                requirement=(
                    "A valid requirement"
                )
            ),

            analysis=sample_analysis(),

            test_cases=sample_test_cases(),
        )


def test_reviewer_rejects_invalid_coverage_score():

    payload = sample_review()

    payload["coverage_score"] = 101

    reviewer = Reviewer(
        FakeLLM(payload)
    )

    with pytest.raises(
        ValueError,
        match="Invalid test-case review structure",
    ):

        reviewer.review(

            requirement=RequirementRequest(
                requirement=(
                    "A valid requirement"
                )
            ),

            analysis=sample_analysis(),

            test_cases=sample_test_cases(),
        )