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

    @staticmethod
    def _normalize_automation_payload(data: object) -> object:
        """Normalize structured LLM automation data to the existing schema."""
        if not isinstance(data, dict):
            return data

        normalized = dict(data)
        cases = normalized.get("automation_cases")

        if not isinstance(cases, list):
            return normalized

        normalized_cases = []

        for case in cases:
            if not isinstance(case, dict):
                normalized_cases.append(case)
                continue

            case = dict(case)

            test_data = case.get("test_data")
            if isinstance(test_data, list):
                case["test_data"] = [
                    {
                        "field": item.get("name", item.get("field", "")),
                        "value": str(item.get("value", "")),
                    }
                    if isinstance(item, dict)
                    else item
                    for item in test_data
                ]

            assertions = case.get("assertions")
            if isinstance(assertions, list):
                case["assertions"] = [
                    AutomationCaseGenerator._automation_item_to_string(item)
                    for item in assertions
                ]

            normalized_cases.append(case)

        normalized["automation_cases"] = normalized_cases
        return normalized

    @staticmethod
    def _automation_item_to_string(item: object) -> str:
        """Convert a structured automation item into readable text."""
        if isinstance(item, str):
            return item

        if isinstance(item, dict):
            preferred_keys = ["type", "selector", "description", "expected", "reason"]
            parts = []

            for key in preferred_keys:
                value = item.get(key)
                if value is not None:
                    if isinstance(value, list):
                        value = ", ".join(str(entry) for entry in value)
                    parts.append(f"{key}: {value}")

            if parts:
                return "; ".join(parts)

            return json.dumps(item, ensure_ascii=False, sort_keys=True)

        return str(item)

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
- Describe the automation approach using normalized automation steps.
- Steps must use one of these exact formats: `goto: URL`, `click: selector`, `fill: selector = value`, or `press: selector = key`.
- Do not use natural-language navigation, click, fill, or keyboard instructions in steps.
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

        data = self._normalize_automation_payload(
            data
        )

        return AutomationCaseResponse.model_validate(
            data
        )
