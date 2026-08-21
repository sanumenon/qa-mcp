from __future__ import annotations

import json

from qa_mcp.core.llm import LLMProvider
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
- Do not invent behavior that is not supported by the requirement.
- Use missing_information from the analysis to avoid pretending unknowns are
  confirmed requirements.
- Steps must be executable by a tester.
- Expected results must be observable and testable.
- IDs must start at TC001 and increment sequentially.
- Do not include markdown or commentary outside the JSON.
"""


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
            payload = json.loads(raw_response)

        except json.JSONDecodeError as exc:

            raise ValueError(
                "LLM returned invalid JSON for test-case generation."
            ) from exc

        response = TestCaseResponse.model_validate(
            payload
        )

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