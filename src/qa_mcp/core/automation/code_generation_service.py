from qa_mcp.models.schemas import (
    AutomationCase,
    GeneratedAutomationArtifact,
)


class AutomationCodeGenerationService:
    """Generate executable automation artifacts from automation cases."""

    def generate(
        self,
        automation_case: AutomationCase,
    ) -> GeneratedAutomationArtifact:
        """Generate executable Python Playwright code."""

        if not automation_case.steps:
            raise ValueError(
                "Automation case must contain at least one step"
            )

        if not automation_case.assertions:
            raise ValueError(
                "Automation case must contain at least one assertion"
            )

        if not automation_case.framework:
            raise ValueError(
                "Automation case must specify a framework"
            )

        if automation_case.framework.lower() != "playwright":
            raise ValueError(
                "Unsupported automation framework: "
                f"{automation_case.framework}"
            )

        function_name = self._function_name(
            automation_case.title
        )

        code = self._generate_playwright_code(
            automation_case,
            function_name,
        )

        return GeneratedAutomationArtifact(
            id="GA001",
            automation_case_id=automation_case.id,
            framework="Playwright",
            language="Python",
            file_name=f"{function_name}.py",
            code=code,
        )

    @staticmethod
    def _function_name(title: str) -> str:
        words = [
            word.lower()
            for word in title.split()
            if word.isalnum()
        ]

        return "test_" + "_".join(words)

    @classmethod
    def _generate_playwright_code(
        cls,
        automation_case: AutomationCase,
        function_name: str,
    ) -> str:
        lines = [
            "from playwright.sync_api import Page, expect",
            "",
            "",
            f"def {function_name}(page: Page):",
        ]

        for step in automation_case.steps:
            lines.append(
                f"    {cls._step_to_code(step)}"
            )

        for assertion in automation_case.assertions:
            lines.append(
                f"    {cls._assertion_to_code(assertion)}"
            )

        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _step_to_code(step: str) -> str:
        if step.startswith("goto: "):
            url = step[6:].strip()

            if not url:
                raise ValueError(
                    "Invalid goto step: URL is required"
                )

            return f'page.goto({url!r})'

        if step.startswith("click: "):
            selector = step[7:].strip()

            if not selector:
                raise ValueError(
                    "Invalid click step: selector is required"
                )

            return (
                f"page.locator({selector!r}).click()"
            )

        if step.startswith("fill: "):
            expression = step[6:].strip()

            if " = " not in expression:
                raise ValueError(
                    "Invalid fill step: expected "
                    "'fill: selector = value'"
                )

            selector, value = expression.split(
                " = ",
                1,
            )

            selector = selector.strip()
            value = value.strip()

            if not selector or not value:
                raise ValueError(
                    "Invalid fill step: selector and value are required"
                )

            return (
                f"page.locator({selector!r}).fill({value!r})"
            )

        if step.startswith("press: "):
            expression = step[7:].strip()

            if " = " not in expression:
                raise ValueError(
                    "Invalid press step: expected "
                    "'press: selector = key'"
                )

            selector, key = expression.split(
                " = ",
                1,
            )

            selector = selector.strip()
            key = key.strip()

            if not selector or not key:
                raise ValueError(
                    "Invalid press step: selector and key are required"
                )

            return (
                f"page.locator({selector!r}).press({key!r})"
            )

        raise ValueError(
            "Unsupported automation step: "
            f"{step}"
        )

    @staticmethod
    def _assertion_to_code(assertion: str) -> str:
        if assertion.startswith("visible: "):
            selector = assertion[9:].strip()

            if not selector:
                raise ValueError(
                    "Invalid visible assertion: selector is required"
                )

            return (
                f"expect(page.locator({selector!r})).to_be_visible()"
            )

        if assertion.startswith("text: "):
            expression = assertion[6:].strip()

            if " = " not in expression:
                raise ValueError(
                    "Invalid text assertion: expected "
                    "'text: selector = expected text'"
                )

            selector, expected = expression.split(
                " = ",
                1,
            )

            selector = selector.strip()
            expected = expected.strip()

            if not selector or not expected:
                raise ValueError(
                    "Invalid text assertion: selector and expected text are required"
                )

            return (
                f"expect(page.locator({selector!r}))."
                f"to_have_text({expected!r})"
            )

        if assertion.startswith("url: "):
            expected_url = assertion[5:].strip()

            if not expected_url:
                raise ValueError(
                    "Invalid url assertion: URL is required"
                )

            return (
                f"expect(page).to_have_url({expected_url!r})"
            )

        raise ValueError(
            "Unsupported automation assertion: "
            f"{assertion}"
        )