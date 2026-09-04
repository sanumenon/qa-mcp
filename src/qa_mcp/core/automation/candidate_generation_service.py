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

        automation_cases = []

        for test_case in test_cases:
            if test_case.id not in candidate_ids:
                continue

            response = (
                self.automation_service.generate_automation(
                    test_case
                )
            )

            if isinstance(response, dict):
                automation_cases.append(
                    response
                )
            else:
                automation_cases.extend(
                    response.automation_cases
                )

        return automation_cases