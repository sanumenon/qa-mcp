class AutomationCandidateGenerationService:
    """Generate automation only for selected automation candidates."""

    def __init__(
        self,
        candidate_service,
        automation_service,
    ):
        self.candidate_service = candidate_service
        self.automation_service = automation_service

    def generate(
        self,
        test_cases,
    ):
        """Select candidates and generate automation for them only."""

        candidate_result = (
            self.candidate_service.select_candidates(
                test_cases
            )
        )

        candidate_ids = set(
            candidate_result.candidate_ids
        )

        return [
            self.automation_service.generate_automation(
                test_case
            )
            for test_case in test_cases
            if test_case.id in candidate_ids
        ]