from qa_mcp.models.schemas import TestCase


class AutomationCandidateSelector:
    """Select test cases suitable for automation."""

    def select_candidates(
        self,
        test_cases: list[TestCase],
    ) -> list[str]:
        """Return IDs of test cases suitable for automation."""

        candidates = []

        for test_case in test_cases:

            if test_case.test_type != "Functional":
                continue

            if test_case.priority not in {
                "High",
                "Medium",
            }:
                continue

            if not test_case.steps:
                continue

            if not test_case.expected_result:
                continue

            candidates.append(
                test_case.id
            )

        return candidates