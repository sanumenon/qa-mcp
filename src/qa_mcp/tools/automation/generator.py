from qa_mcp.core.json_response import parse_json_response

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
- For UI/browser automation, the framework MUST be "Playwright".
- Do not select Selenium, WebDriver, Cypress, Puppeteer, or any other UI framework.
- Use "Playwright" as the framework whenever the test case is suitable for browser/UI automation.
- For email validation, API calls, or other supporting interactions, do not replace Playwright as the primary UI framework.
- If a supporting capability is required but is not available in the requirement, record it in limitations rather than selecting another automation framework.
"""

        response = self.llm.generate(
            prompt
        )

        try:
            data = parse_json_response(
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