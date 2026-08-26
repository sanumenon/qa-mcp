from qa_mcp.models.schemas import (
    AutomationCaseResponse,
    TestCase,
)


class AutomationService:
    """Application service for automation case generation."""

    def __init__(self, generator):
        self.generator = generator

    def generate_automation(
        self,
        test_case: TestCase,
    ) -> AutomationCaseResponse:
        """Generate automation candidates for a test case."""

        return self.generator.generate(
            test_case
        )