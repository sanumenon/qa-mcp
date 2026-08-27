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
        """Generate a Python Playwright artifact."""

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
            id=f"GA001",
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

        return (
            "test_"
            + "_".join(words)
        )

    @staticmethod
    def _generate_playwright_code(
        automation_case: AutomationCase,
        function_name: str,
    ) -> str:

        lines = [
            "from playwright.sync_api import Page",
            "",
            "",
            f"def {function_name}(page: Page):",
        ]

        for step in automation_case.steps:
            lines.append(
                f"    # {step}"
            )

        for assertion in automation_case.assertions:
            lines.append(
                f"    # Assert: {assertion}"
            )

        lines.append("")

        return "\n".join(lines)
