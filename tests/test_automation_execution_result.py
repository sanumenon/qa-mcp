from qa_mcp.models.schemas import AutomationExecutionResult


def test_automation_execution_result_contains_execution_metadata():

    result = AutomationExecutionResult(
        execution_id="EX001",
        automation_artifact_id="GA001",
        automation_case_id="AC001",
        status="PASSED",
        exit_code=0,
        stdout="1 passed",
        stderr="",
        duration_seconds=1.25,
    )

    assert result.execution_id == "EX001"
    assert result.automation_artifact_id == "GA001"
    assert result.automation_case_id == "AC001"
    assert result.status == "PASSED"
    assert result.exit_code == 0
    assert result.stdout == "1 passed"
    assert result.stderr == ""
    assert result.duration_seconds == 1.25