import json

from qa_mcp.models.schemas import (
    AutomationCaseResponse,
    TestCase,
)


class AutomationCaseGenerator:
    """Generate structured automation candidates from test cases."""

    def __init__(self, llm):
        self.llm = llm

    def generate(
        self,
        test_case: TestCase,
    ) -> AutomationCaseResponse:

        prompt = f"""
Generate an automation candidate for the following test case.

Test case:
{test_case.model_dump_json(indent=2)}

Return JSON only using this structure:

{{
    "automation_cases": [
        {{
            "id": "AC001",
            "test_case_id": "{test_case.id}",
            "title": "",
            "automation_type": "",
            "framework": "",
            "priority": "",
            "confidence": "",
            "preconditions": [],
            "test_data": [],
            "steps": [],
            "assertions": [],
            "limitations": []
        }}
    ]
}}

Rules:
- Preserve the source test case ID.
- Do not invent requirements.
- Do not generate executable automation code.
- Describe the automation approach only.
- Keep the steps executable and specific.
- Keep assertions observable.
"""

        response = self.llm.generate(
            prompt
        )

        try:
            data = json.loads(
                response
            )
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            raise ValueError(
                "Invalid automation generation response"
            )

        return AutomationCaseResponse.model_validate(
            data
        )