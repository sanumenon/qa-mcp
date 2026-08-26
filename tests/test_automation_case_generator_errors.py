import pytest

from qa_mcp.models.schemas import (
    TestCase as QATestCase,
)

from qa_mcp.tools.automation.generator import (
    AutomationCaseGenerator,
)


class InvalidJSONLLM:

    def generate(self, prompt: str) -> str:
        return "this is not valid json"


def test_automation_case_generator_rejects_invalid_llm_json():

    llm = InvalidJSONLLM()

    generator = AutomationCaseGenerator(llm)

    test_case = QATestCase(
        id="TC001",
        title="Successful login",
        test_type="Functional",
        priority="High",
        preconditions=[
            "User account exists"
        ],
        steps=[
            "Open login page",
            "Enter valid username",
            "Enter valid password",
            "Click Login",
        ],
        expected_result="User is redirected to dashboard",
    )

    with pytest.raises(
        ValueError,
        match="Invalid automation generation response",
    ):
        generator.generate(
            test_case
        )