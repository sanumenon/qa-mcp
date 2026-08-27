from qa_mcp.models.schemas import (
    AutomationCase,
    AutomationValidationResult,
)


class AutomationValidator:

    def validate(
        self,
        automation_case: AutomationCase,
    ) -> AutomationValidationResult:

        errors = []

        if not automation_case.steps:
            errors.append(
                "Automation case must contain at least one step"
            )

        if not automation_case.assertions:
            errors.append(
                "Automation case must contain at least one assertion"
            )

        if not automation_case.framework:
            errors.append(
                "Automation case must specify a framework"
            )

        return AutomationValidationResult(
            automation_case_id=automation_case.id,
            test_case_id=automation_case.test_case_id,
            valid=not errors,
            errors=errors,
            warnings=[],
        )