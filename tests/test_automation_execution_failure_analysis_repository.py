from qa_mcp.infrastructure.sqlite_automation_execution_repository import (
    SQLiteAutomationExecutionRepository,
)
from qa_mcp.models.schemas import AutomationExecutionResult


def make_result(
    execution_id,
    case_id,
    status,
    duration,
    exit_code,
    stdout="",
    stderr="",
    error=None,
):
    return AutomationExecutionResult(
        execution_id=execution_id,
        automation_artifact_id=f"GA-{execution_id}",
        automation_case_id=case_id,
        status=status,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=duration,
        error=error,
    )


def test_failure_analysis_aggregates_failures(tmp_path):
    repository = SQLiteAutomationExecutionRepository(
        database_path=str(tmp_path / "failures.db")
    )

    repository.save(
        make_result(
            "EX001", "AC001", "PASSED", 1.0, 0,
            stdout="1 passed",
        )
    )
    repository.save(
        make_result(
            "EX002", "AC001", "FAILED", 2.0, 1,
            stderr="assertion failed",
        )
    )
    repository.save(
        make_result(
            "EX003", "AC002", "ERROR", 3.0, None,
            error="browser launch error",
        )
    )
    repository.save(
        make_result(
            "EX004", "AC002", "NOT_EXECUTED", 0.0, None,
        )
    )

    result = repository.analyze_failures()

    assert result.total_executions == 4
    assert result.failed_executions == 1
    assert result.error_executions == 1
    assert result.total_failures == 2
    assert result.failure_rate_percent == 50.0
    assert result.affected_automation_cases == [
        "AC001",
        "AC002",
    ]
    assert result.latest_failure_execution_id == "EX003"
    assert result.latest_failure_status == "ERROR"

    assert len(result.failures) == 2
    assert result.failures[0].execution_id == "EX003"
    assert result.failures[0].message == "browser launch error"
    assert result.failures[1].execution_id == "EX002"
    assert result.failures[1].message == "assertion failed"


def test_failure_analysis_filters_by_automation_case(tmp_path):
    repository = SQLiteAutomationExecutionRepository(
        database_path=str(tmp_path / "failure-filter.db")
    )

    repository.save(
        make_result(
            "EX001", "AC001", "FAILED", 1.0, 1,
            stderr="AC001 failure",
        )
    )
    repository.save(
        make_result(
            "EX002", "AC002", "ERROR", 2.0, None,
            error="AC002 error",
        )
    )

    result = repository.analyze_failures(
        automation_case_id="AC001"
    )

    assert result.total_executions == 1
    assert result.total_failures == 1
    assert result.failed_executions == 1
    assert result.error_executions == 0
    assert result.failure_rate_percent == 100.0
    assert result.affected_automation_cases == ["AC001"]
    assert result.failures[0].execution_id == "EX001"


def test_failure_analysis_respects_limit(tmp_path):
    repository = SQLiteAutomationExecutionRepository(
        database_path=str(tmp_path / "failure-limit.db")
    )

    for index in range(1, 4):
        repository.save(
            make_result(
                f"EX00{index}",
                "AC001",
                "FAILED",
                1.0,
                1,
                stderr=f"failure-{index}",
            )
        )

    result = repository.analyze_failures(limit=2)

    assert result.total_failures == 3
    assert len(result.failures) == 2
    assert result.failures[0].execution_id == "EX003"
    assert result.failures[1].execution_id == "EX002"


def test_failure_analysis_empty(tmp_path):
    repository = SQLiteAutomationExecutionRepository(
        database_path=str(tmp_path / "failure-empty.db")
    )

    result = repository.analyze_failures()

    assert result.total_executions == 0
    assert result.failed_executions == 0
    assert result.error_executions == 0
    assert result.total_failures == 0
    assert result.failure_rate_percent == 0.0
    assert result.affected_automation_cases == []
    assert result.latest_failure_execution_id is None
    assert result.latest_failure_status is None
    assert result.failures == []
