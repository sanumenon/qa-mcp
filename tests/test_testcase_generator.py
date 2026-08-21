import json

import pytest

from qa_mcp.models.schemas import (
    RequirementAnalysis,
    RequirementRequest,
    TestCaseGenerationRequest as GenerationRequest,
)

from qa_mcp.tools.testcase.generator import (
    TestCaseGenerator as Generator,
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

    return {

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
                    "defined account-discovery policy."
                ),
            },
        ]
    }


def build_request():

    return GenerationRequest(

        requirement=RequirementRequest(

            requirement=(
                "User can reset password "
                "using email."
            ),

            application="Customer Portal",
        ),

        analysis=sample_analysis(),
    )


def test_generator_returns_structured_test_cases():

    fake_llm = FakeLLM(
        sample_test_cases()
    )

    generator = Generator(
        fake_llm
    )

    result = generator.generate(
        build_request()
    )

    assert len(
        result.test_cases
    ) == 2

    assert (
        result.test_cases[0].id
        == "TC001"
    )

    assert (
        result.test_cases[0].test_type
        == "Functional"
    )

    assert (
        result.test_cases[1].id
        == "TC002"
    )

    assert (
        "Customer Portal"
        in fake_llm.last_prompt
    )

    assert (
        "reset password"
        in fake_llm.last_prompt
    )


def test_generator_rejects_invalid_json():

    class InvalidLLM:

        def generate(
            self,
            prompt: str,
        ) -> str:

            return "not-json"

    generator = Generator(
        InvalidLLM()
    )

    with pytest.raises(
        ValueError,
        match="invalid JSON",
    ):

        generator.generate(
            build_request()
        )


def test_generator_rejects_non_sequential_ids():

    payload = sample_test_cases()

    payload["test_cases"][1][
        "id"
    ] = "TC003"

    generator = Generator(
        FakeLLM(payload)
    )

    with pytest.raises(
        ValueError,
        match="sequential starting from TC001",
    ):

        generator.generate(
            build_request()
        )