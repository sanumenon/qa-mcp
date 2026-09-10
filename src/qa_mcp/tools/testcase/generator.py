from __future__ import annotations

import json
import logging

from pydantic import ValidationError

from qa_mcp.core.json_response import parse_json_response

from qa_mcp.core.llm import (
    LLMGenerationError,
    LLMProvider,
)
from qa_mcp.models.schemas import (
    TestCaseGenerationRequest,
    TestCaseResponse,
)


GENERATOR_PROMPT = """You are a senior QA automation engineer.

Generate comprehensive, independent test cases from the supplied requirement
and requirement analysis.

Application:
{application}

Requirement:
{requirement}

Requirement analysis:
{analysis}

Return ONLY valid JSON with exactly this structure:

{{
  "test_cases": [
    {{
      "id": "TC001",
      "title": "short test case title",
      "priority": "High|Medium|Low",
      "test_type": "Functional|Negative|Boundary|Integration|Security|Accessibility|Performance|API",
      "preconditions": [],
      "steps": [],
      "expected_result": "clear expected result"
    }}
  ]
}}

Rules:
- Each test case must test one clear behavior.
- Cover positive, negative and applicable boundary scenarios.
- Generate a complete test-case suite for the supplied requirement analysis.
- Collectively cover every materially distinct scenario in the supplied
  positive_scenarios, negative_scenarios, and edge_cases.
- Each materially distinct scenario must be represented by at least one
  appropriate test case.
- Multiple scenarios may be combined into one test case only when the
  resulting test case still clearly verifies each scenario.
- Do not stop after generating one or a small subset of scenarios.
- Before returning the response, verify that the generated test-case suite
  provides coverage across all supplied scenario categories.
- Do not invent behavior that is not supported by the requirement.
- Use missing_information from the analysis to avoid pretending unknowns are
  confirmed requirements.
- Steps must be executable by a tester.
- Expected results must be observable and testable.
- IDs must start at TC001 and increment sequentially.
- The response must always use the required "test_cases" wrapper.
- Never return a single test-case object without the "test_cases" wrapper.
- Do not include markdown or commentary outside the JSON.
"""


logger = logging.getLogger(__name__)


class TestCaseGenerator:

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def generate(
        self,
        request: TestCaseGenerationRequest,
    ) -> TestCaseResponse:

        analysis_json = request.analysis.model_dump_json(
            indent=2
        )

        prompt = GENERATOR_PROMPT.format(
            application=request.requirement.application,
            requirement=request.requirement.requirement,
            analysis=analysis_json,
        )

        raw_response = self.llm.generate(prompt)

        try:
            payload = parse_json_response(raw_response)

        except json.JSONDecodeError as exc:

            logger.error(
                "QA test-case generation failed: LLM returned unusable "
                "non-JSON response. Provider response: %r",
                raw_response,
            )

            raise LLMGenerationError(
                "LLM returned an unusable response for test-case generation.",
                provider_response=raw_response,
            ) from exc

        if not isinstance(payload, dict):
            raise LLMGenerationError(
                "LLM returned an invalid test-case generation payload."
            )

        if "test_cases" not in payload:
            raise LLMGenerationError(
                "LLM returned an incomplete test-case generation payload."
            )

        if not isinstance(payload["test_cases"], list):
            raise LLMGenerationError(
                "LLM returned an invalid test_cases collection."
            )

        if not payload["test_cases"]:
            raise LLMGenerationError(
                "LLM returned no test cases."
            )

        try:
            response = TestCaseResponse.model_validate(
                payload
            )
        except ValidationError as exc:
            raise LLMGenerationError(
                "LLM returned an invalid test-case generation payload."
            ) from exc

        self._validate_ids(response)

        return response

    @staticmethod
    def _validate_ids(
        response: TestCaseResponse,
    ) -> None:

        expected_ids = [
            f"TC{index:03d}"
            for index in range(
                1,
                len(response.test_cases) + 1,
            )
        ]

        actual_ids = [
            test_case.id
            for test_case in response.test_cases
        ]

        if actual_ids != expected_ids:

            raise ValueError(
                "Test case IDs must be sequential "
                "starting from TC001."
            )