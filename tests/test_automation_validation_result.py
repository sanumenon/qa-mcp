from qa_mcp.models.schemas import (
    AutomationCase,
    AutomationValidationResult,
)


def test_automation_validation_result_can_represent_valid_case():

    result = AutomationValidationResult(
        automation_case_id="AC001",
        test_case_id="TC001",
        valid=True,
        errors=[],
        warnings=[],
    )

    assert result.automation_case_id == "AC001"
    assert result.test_case_id == "TC001"
    assert result.valid is True
    assert result.errors == []
    assert result.warnings == []