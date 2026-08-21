from __future__ import annotations

from qa_mcp.core.llm import LLMProvider
from qa_mcp.models.schemas import (
    QASuiteResult,
    RequirementRequest,
    TestCaseGenerationRequest,
)

from qa_mcp.tools.requirement.analyzer import (
    RequirementAnalyzer,
)

from qa_mcp.tools.testcase.generator import (
    TestCaseGenerator,
)

from qa_mcp.tools.testcase.reviewer import (
    TestCaseReviewer,
)


class QASuiteWorkflow:

    def __init__(
        self,
        llm: LLMProvider,
    ):

        self.requirement_analyzer = (
            RequirementAnalyzer(llm)
        )

        self.testcase_generator = (
            TestCaseGenerator(llm)
        )

        self.testcase_reviewer = (
            TestCaseReviewer(llm)
        )

    def run(
        self,
        requirement: RequirementRequest,
    ) -> QASuiteResult:

        # ----------------------------------------
        # Step 1: Analyze requirement
        # ----------------------------------------

        analysis = (
            self.requirement_analyzer.analyze(
                requirement
            )
        )

        # ----------------------------------------
        # Step 2: Generate test cases
        # ----------------------------------------

        generation_request = (
            TestCaseGenerationRequest(
                requirement=requirement,
                analysis=analysis,
            )
        )

        test_cases = (
            self.testcase_generator.generate(
                generation_request
            )
        )

        # ----------------------------------------
        # Step 3: Review test cases
        # ----------------------------------------

        review = (
            self.testcase_reviewer.review(
                requirement=requirement,
                analysis=analysis,
                test_cases=test_cases,
            )
        )

        # ----------------------------------------
        # Step 4: Return complete QA suite
        # ----------------------------------------

        return QASuiteResult(
            requirement=requirement,
            analysis=analysis,
            test_cases=test_cases,
            review=review,
        )