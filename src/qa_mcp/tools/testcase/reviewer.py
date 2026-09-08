from __future__ import annotations

import json

from qa_mcp.core.json_response import parse_json_response
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
- duplicate_test_cases MUST contain strings only.
- missing_scenarios MUST contain strings only.
- weak_test_cases MUST contain strings only.
- requirement_gaps MUST contain strings only.
- priority_issues MUST contain strings only.
- recommendations MUST contain strings only.
- Do not return objects inside any of these arrays.
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
            payload = parse_json_response(
                raw_response
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON "
                "for test-case review."
            ) from exc

        payload = self._normalize_review_payload(
            payload
        )

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

    @staticmethod
    def _normalize_review_payload(
        payload: object,
    ) -> object:
        """Normalize structured LLM review items to the existing string schema."""

        if not isinstance(payload, dict):
            return payload

        list_fields = [
            "duplicate_test_cases",
            "missing_scenarios",
            "weak_test_cases",
            "requirement_gaps",
            "priority_issues",
            "recommendations",
        ]

        normalized = dict(payload)

        for field in list_fields:
            value = normalized.get(field)

            if not isinstance(value, list):
                continue

            normalized[field] = [
                TestCaseReviewer._review_item_to_string(
                    item
                )
                for item in value
            ]

        return normalized

    @staticmethod
    def _review_item_to_string(
        item: object,
    ) -> str:
        """Convert a string or structured review item into readable text."""

        if isinstance(item, str):
            return item

        if isinstance(item, dict):
            if item.get("id") is not None and item.get("reason") is not None:
                return (
                    f"{item['id']}: "
                    f"{item['reason']}"
                )

            preferred_keys = [
                "scenario",
                "issue",
                "gap",
                "recommendation",
                "reason",
                "description",
            ]

            parts = []

            for key in preferred_keys:
                value = item.get(key)

                if value is not None:
                    if isinstance(value, list):
                        value = ", ".join(
                            str(entry)
                            for entry in value
                        )

                    parts.append(
                        f"{key}: {value}"
                    )

            if parts:
                return "; ".join(parts)

            return json.dumps(
                item,
                ensure_ascii=False,
                sort_keys=True,
            )

        return str(item)
