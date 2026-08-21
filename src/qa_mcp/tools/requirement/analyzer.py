from __future__ import annotations

import json

from qa_mcp.core.llm import LLMProvider
from qa_mcp.models.schemas import (
    RequirementAnalysis,
    RequirementRequest,
)


ANALYSIS_PROMPT = """You are a senior QA engineer analyzing a software requirement.

Application:
{application}

Requirement:
{requirement}

Analyze the requirement for test design.

Return ONLY valid JSON with exactly these fields:

{{
  "summary": "short requirement summary",
  "actors": [],
  "functional_requirements": [],
  "business_rules": [],
  "preconditions": [],
  "main_workflows": [],
  "positive_scenarios": [],
  "negative_scenarios": [],
  "edge_cases": [],
  "missing_information": [],
  "recommended_test_types": []
}}

Rules:

- Do not invent confirmed business rules.
- Put assumptions or unknowns in missing_information.
- Keep scenarios concise and testable.
- recommended_test_types may include:
  functional,
  negative,
  boundary,
  integration,
  security,
  usability,
  accessibility,
  performance,
  API.
"""


class RequirementAnalyzer:

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def analyze(
        self,
        request: RequirementRequest,
    ) -> RequirementAnalysis:

        prompt = ANALYSIS_PROMPT.format(
            application=request.application,
            requirement=request.requirement,
        )

        raw_response = self.llm.generate(prompt)

        try:
            payload = json.loads(raw_response)

        except json.JSONDecodeError as exc:

            raise ValueError(
                "LLM returned invalid JSON for requirement analysis."
            ) from exc

        return RequirementAnalysis.model_validate(payload)