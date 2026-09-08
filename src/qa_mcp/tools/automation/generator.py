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

            steps = case.get("steps")
            limitations = case.get("limitations")

            if not isinstance(limitations, list):
                limitations = []

            if isinstance(steps, list):
                normalized_steps = []

                for step in steps:
                    normalized_step = (
                        AutomationCaseGenerator._normalize_step(step)
                    )

                    if normalized_step is not None:
                        normalized_steps.append(normalized_step)
                    elif isinstance(step, str) and step.strip():
                        limitations.append(step.strip())

                case["steps"] = normalized_steps

            case["limitations"] = [
                str(item)
                for item in limitations
                if str(item).strip()
            ]

            test_data = case.get("test_data")

            if isinstance(test_data, list):
                case["test_data"] = [
                    {
                        "field": item.get(
                            "name",
                            item.get("field", ""),
                        ),
                        "value": str(
                            item.get("value", "")
                        ),
                    }
                    if isinstance(item, dict)
                    else item
                    for item in test_data
                ]

            assertions = case.get("assertions")

            if isinstance(assertions, list):
                case["assertions"] = [
                    AutomationCaseGenerator._normalize_assertion(item)
                    for item in assertions
                ]

            normalized_cases.append(case)

        normalized["automation_cases"] = normalized_cases
        return normalized

    @staticmethod
    def _normalize_step(step: object) -> str | None:
        """Normalize supported structured steps and reject non-executable steps."""
        if not isinstance(step, str):
            return None

        value = step.strip()

        if not value:
            return None

        if (
            value.startswith("goto: ")
            or value.startswith("click: ")
            or value.startswith("fill: ")
            or value.startswith("press: ")
        ):
            return value

        return None

    @staticmethod
    def _normalize_assertion(assertion: object) -> str:
        """Normalize structured assertions to the code-generation schema."""
        if isinstance(assertion, str):
            value = assertion.strip()

            if value.startswith(
                ("visible: ", "text: ", "url: ")
            ):
                return value

            return value

        if isinstance(assertion, dict):
            assertion_type = assertion.get("type")
            selector = assertion.get("selector")
            expected = assertion.get("expected")

            if assertion_type in (
                "element_visible",
                "visible",
            ):
                if selector:
                    return f"visible: {selector}"

            if assertion_type in (
                "text",
                "element_text",
                "text_equals",
            ):
                if selector and expected is not None:
                    return (
                        f"text: {selector} = {expected}"
                    )

            if assertion_type in (
                "url",
                "url_equals",
            ):
                if expected:
                    return f"url: {expected}"

            return (
                AutomationCaseGenerator
                ._automation_item_to_string(assertion)
            )

        return str(assertion)

    @staticmethod
    def _automation_item_to_string(item: object) -> str:
        """Convert a structured automation item into readable text."""
        if isinstance(item, str):
            return item

        if isinstance(item, dict):
            preferred_keys = [
                "type",
                "selector",
                "description",
                "expected",
                "reason",
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
