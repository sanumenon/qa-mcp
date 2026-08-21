from __future__ import annotations

import json

from qa_mcp.core.llm import LLMProvider

from qa_mcp.models.schemas import (
    RequirementAnalysis,
    RequirementRequest,
    TestCaseResponse,
    TestCaseReview,
)


REVIEW_PROMPT = """You are a senior QA lead reviewing a generated test suite.

Application:
{application}

Requirement:
{requirement}

Requirement analysis:
{analysis}

Generated test cases:
{test_cases}

Review the suite for completeness and quality.

Return ONLY valid JSON with exactly this structure:

{{
  "overall_quality": "Excellent|Good|Needs Improvement|Poor",
  "coverage_score": 0,
  "duplicate_test_cases": [],
  "missing_scenarios": [],
  "weak_test_cases": [],
  "requirement_gaps": [],
  "priority_issues": [],
  "recommendations": [],
  "summary": "short review summary"
}}

Rules:
- coverage_score must be an integer from 0 to 100.
- Identify meaningful gaps, not hypothetical features.
- Do not invent confirmed requirements.
- Treat information listed as missing in the analysis as unknown.
- A weak test case is one whose steps or expected result are not sufficiently
  clear or testable.
- Identify duplicate or substantially overlapping test cases.
- Recommendations must be actionable.
- Return JSON only.
"""


class TestCaseReviewer:

    def __init__(
        self,
        llm: LLMProvider,
    ):
        self.llm = llm

    def review(
        self,
        requirement: RequirementRequest,
        analysis: RequirementAnalysis,
        test_cases: TestCaseResponse,
    ) -> TestCaseReview:

        prompt = REVIEW_PROMPT.format(
            application=requirement.application,
            requirement=requirement.requirement,
            analysis=analysis.model_dump_json(
                indent=2
            ),
            test_cases=test_cases.model_dump_json(
                indent=2
            ),
        )

        raw_response = self.llm.generate(
            prompt
        )

        try:

            payload = json.loads(
                raw_response
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "LLM returned invalid JSON "
                "for test-case review."
            ) from exc

        try:

            review = TestCaseReview.model_validate(
                payload
            )

        except Exception as exc:

            raise ValueError(
                "Invalid test-case review "
                f"structure: {exc}"
            ) from exc

        return review