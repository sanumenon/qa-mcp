from qa_mcp.models.schemas import (
    AutomationCandidateResult,
    TestCase,
)

from qa_mcp.core.automation.candidate_selector import (
    AutomationCandidateSelector,
)


class AutomationCandidateService:
    """Service for selecting automation candidates."""

    def __init__(
        self,
        selector: AutomationCandidateSelector,
    ):
        self.selector = selector

    def select_candidates(
        self,
        test_cases: list[TestCase],
    ) -> AutomationCandidateResult:
        """Select automation candidates from test cases."""

        candidate_ids = self.selector.select_candidates(
            test_cases
        )

        candidate_id_set = set(
            candidate_ids
        )

        manual_ids = [
            test_case.id
            for test_case in test_cases
            if test_case.id not in candidate_id_set
        ]

        return AutomationCandidateResult(
            candidate_ids=candidate_ids,
            manual_ids=manual_ids,
            total=len(test_cases),
        )