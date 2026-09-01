from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Protocol


class LLMProvider(Protocol):
    """Common interface used by all LLM providers."""

    def generate(self, prompt: str) -> str:
        """Generate a text response for the supplied prompt."""
        ...


@dataclass
class MockLLM:
    """Deterministic local provider used for development and tests."""

    response: str | None = None

    def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if self.response is not None:
            return self.response

        if (
            "Return ONLY valid JSON with exactly this structure:"
            in prompt
            and '"overall_quality"' in prompt
        ):
            return self._test_case_review()

        if (
            "Return ONLY valid JSON with exactly this structure:"
            in prompt
            and '"test_cases"' in prompt
        ):
            return self._test_case_generation()

        if (
            "Return ONLY valid JSON with exactly these fields:"
            in prompt
            and '"summary"' in prompt
            and '"actors"' in prompt
        ):
            return self._requirement_analysis()

        return "{}"

    @staticmethod
    def _requirement_analysis() -> str:
        return """
{
  "summary": "User password reset using a time-limited single-use email link.",
  "actors": [
    "Registered user",
    "Password reset service",
    "Email service"
  ],
  "functional_requirements": [
    "A registered user can request a password reset.",
    "The system sends a password-reset link to the registered user's email address.",
    "The password-reset link expires after 30 minutes.",
    "The password-reset link can only be used once."
  ],
  "business_rules": [
    "The password-reset link expires after 30 minutes.",
    "A password-reset link can only be used once."
  ],
  "preconditions": [
    "The user has a registered account.",
    "The registered user has an accessible email address."
  ],
  "main_workflows": [
    "Request password reset.",
    "Receive password-reset email.",
    "Open the password-reset link.",
    "Complete password reset."
  ],
  "positive_scenarios": [
    "Registered user successfully requests a password reset.",
    "Registered user opens a valid password-reset link and resets the password."
  ],
  "negative_scenarios": [
    "Unregistered user attempts to request a password reset.",
    "User attempts to use an expired password-reset link.",
    "User attempts to reuse a password-reset link."
  ],
  "edge_cases": [
    "Password-reset link is used close to the 30-minute expiration boundary.",
    "User opens the same password-reset link more than once."
  ],
  "missing_information": [
    "Password complexity requirements are not specified.",
    "The behavior for requesting multiple password-reset links is not specified.",
    "The behavior when the reset email cannot be delivered is not specified."
  ],
  "recommended_test_types": [
    "functional",
    "negative",
    "boundary",
    "security",
    "integration"
  ]
}
""".strip()

    @staticmethod
    def _test_case_generation() -> str:
        return """
{
  "test_cases": [
    {
      "id": "TC001",
      "title": "Registered user requests password reset",
      "priority": "High",
      "test_type": "Functional",
      "preconditions": [
        "A registered user account exists."
      ],
      "steps": [
        "Navigate to the password reset page.",
        "Enter the registered user's email address.",
        "Submit the password reset request."
      ],
      "expected_result": "The system accepts the request and sends a password-reset link to the registered user's email address."
    },
    {
      "id": "TC002",
      "title": "Registered user resets password with valid link",
      "priority": "High",
      "test_type": "Functional",
      "preconditions": [
        "A registered user has received a valid password-reset link."
      ],
      "steps": [
        "Open the password-reset link within 30 minutes.",
        "Enter a new password.",
        "Submit the password reset."
      ],
      "expected_result": "The password is reset successfully and the password-reset link is no longer usable."
    },
    {
      "id": "TC003",
      "title": "Expired password-reset link is rejected",
      "priority": "High",
      "test_type": "Boundary",
      "preconditions": [
        "A password-reset link was issued more than 30 minutes ago."
      ],
      "steps": [
        "Open the password-reset link after the 30-minute expiration period."
      ],
      "expected_result": "The system rejects the expired password-reset link and does not allow the password to be reset."
    },
    {
      "id": "TC004",
      "title": "Password-reset link cannot be reused",
      "priority": "High",
      "test_type": "Security",
      "preconditions": [
        "A password-reset link has already been successfully used."
      ],
      "steps": [
        "Open the previously used password-reset link again."
      ],
      "expected_result": "The system rejects the previously used link and does not allow another password reset."
    },
    {
      "id": "TC005",
      "title": "Unregistered user requests password reset",
      "priority": "Medium",
      "test_type": "Negative",
      "preconditions": [
        "The supplied email address is not associated with a registered account."
      ],
      "steps": [
        "Navigate to the password reset page.",
        "Enter an unregistered email address.",
        "Submit the password reset request."
      ],
      "expected_result": "The system does not create a password-reset capability for the unregistered account."
    }
  ]
}
""".strip()

    @staticmethod
    def _test_case_review() -> str:
        return """
{
  "overall_quality": "Good",
  "coverage_score": 92,
  "duplicate_test_cases": [],
  "missing_scenarios": [
    "Password-reset email delivery failure behavior is not specified.",
    "Behavior for multiple password-reset requests is not specified."
  ],
  "weak_test_cases": [],
  "requirement_gaps": [
    "Password complexity requirements are not specified."
  ],
  "priority_issues": [],
  "recommendations": [
    "Define password complexity requirements.",
    "Define behavior when password-reset email delivery fails.",
    "Define behavior when multiple reset links are requested."
  ],
  "summary": "The generated suite covers the core password reset flow, expiration boundary, single-use restriction, and negative behavior."
}
""".strip()

class BedrockLLM:
    """AWS Bedrock provider."""

    def __init__(self, region: str, model_id: str):
        if not region:
            raise ValueError("AWS region is required for Bedrock.")

        if not model_id:
            raise ValueError("Bedrock model ID is required.")

        import boto3

        self.model_id = model_id
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region,
        )

    def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        payload = json.loads(response["body"].read())

        content = payload.get("content", [])

        return "".join(
            item.get("text", "")
            for item in content
            if item.get("type") == "text"
        )


def create_llm(config: dict) -> LLMProvider:
    """Create the configured LLM provider."""

    provider = config.get("llm", {}).get(
        "provider",
        "mock",
    ).lower()

    if provider == "mock":
        return MockLLM()

    if provider == "bedrock":
        llm_config = config.get("llm", {})

        region = os.getenv(
            "AWS_REGION",
            llm_config.get("region", ""),
        )

        model_id = os.getenv(
            "BEDROCK_MODEL_ID",
            llm_config.get("model_id", ""),
        )

        return BedrockLLM(
            region=region,
            model_id=model_id,
        )

    raise ValueError(
        f"Unsupported LLM provider: {provider}. "
        "Supported providers: mock, bedrock."
    )