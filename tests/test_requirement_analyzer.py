import json

from qa_mcp.models.schemas import RequirementRequest
from qa_mcp.tools.requirement.analyzer import RequirementAnalyzer


class FakeLLM:

    def __init__(self, payload: dict):
        self.payload = payload
        self.last_prompt:str = ""

    def generate(self, prompt: str) -> str:

        self.last_prompt = prompt

        return json.dumps(self.payload)


def sample_payload():

    return {
        "summary": (
            "User can reset a password "
            "using registered email."
        ),

        "actors": [
            "Registered User"
        ],

        "functional_requirements": [
            "User can request a password reset."
        ],

        "business_rules": [],

        "preconditions": [
            "User has a registered account."
        ],

        "main_workflows": [
            "Request password reset"
        ],

        "positive_scenarios": [
            "Registered email receives reset instructions."
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
    }


def test_requirement_analyzer_returns_structured_analysis():

    fake_llm = FakeLLM(
        sample_payload()
    )

    analyzer = RequirementAnalyzer(
        fake_llm
    )

    result = analyzer.analyze(
        RequirementRequest(
            requirement=(
                "User can reset password "
                "using email."
            ),
            application="Customer Portal",
        )
    )

    assert result.summary.startswith(
        "User can reset"
    )

    assert result.actors == [
        "Registered User"
    ]

    assert "functional" in (
        result.recommended_test_types
    )

    assert "Customer Portal" in (
        fake_llm.last_prompt
    )

    assert "reset password" in (
        fake_llm.last_prompt
    )


def test_requirement_analyzer_rejects_invalid_llm_json():

    class InvalidLLM:

        def generate(self, prompt: str) -> str:
            return "not-json"

    analyzer = RequirementAnalyzer(
        InvalidLLM()
    )

    try:

        analyzer.analyze(
            RequirementRequest(
                requirement="A valid requirement"
            )
        )

        assert False, (
            "Expected ValueError"
        )

    except ValueError as exc:

        assert "invalid JSON" in str(exc)