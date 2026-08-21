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

    response: str = "MOCK_LLM_RESPONSE"

    def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        return self.response


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