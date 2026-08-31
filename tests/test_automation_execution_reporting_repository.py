from qa_mcp.infrastructure.sqlite_automation_execution_repository import (
    SQLiteAutomationExecutionRepository,
)
from qa_mcp.models.schemas import (
    AutomationExecutionResult,
)


def make_result(
    execution_id,
    case_id,
    status,
    duration,
    exit_code,
):
    return AutomationExecutionResult(
        execution_id=execution_id,
        automation_artifact_id=f"GA-{execution_id}",
        automation_case_id=case_id,
        status=status,
        exit_code=exit_code,
        stdout="",
        stderr="",
        duration_seconds=duration,
        error=None,
    )


def test_repository_report_aggregates_execution_history(
    tmp_path,
):
    repository = SQLiteAutomationExecutionRepository(
        database_path=str(
            tmp_path / "reporting.db"
        )
    )

    repository.save(
        make_result(
            "EX001",
            "AC001",
            "PASSED",
            1.0,
            0,
        )
    )

    repository.save(
        make_result(
            "EX002",
            "AC001",
            "FAILED",
            2.0,
            1,
        )
    )

    repository.save(
        make_result(
            "EX003",
            "AC001",
            "NOT_EXECUTED",
            3.0,
            None,
        )
    )

    repository.save(
        make_result(
            "EX004",
            "AC001",
            "ERROR",
            4.0,
            None,
        )
    )

    report = repository.report()

    assert report.total_executions == 4
    assert report.passed == 1
    assert report.failed == 1
    assert report.not_executed == 1
    assert report.error == 1
    assert report.pass_rate_percent == 25.0
    assert report.total_duration_seconds == 10.0
    assert report.average_duration_seconds == 2.5
    assert report.latest_execution_id == "EX004"
    assert report.latest_status == "ERROR"


def test_repository_report_filters_by_automation_case(
    tmp_path,
):
    repository = SQLiteAutomationExecutionRepository(
        database_path=str(
            tmp_path / "reporting-filter.db"
        )
    )

    repository.save(
        make_result(
            "EX001",
            "AC001",
            "PASSED",
            1.0,
            0,
        )
    )

    repository.save(
        make_result(
            "EX002",
            "AC002",
            "FAILED",
            2.0,
            1,
        )
    )

    report = repository.report(
        automation_case_id="AC001"
    )

    assert report.total_executions == 1
    assert report.passed == 1
    assert report.failed == 0
    assert report.pass_rate_percent == 100.0
    assert report.latest_execution_id == "EX001"


def test_repository_report_is_empty_when_no_executions(
    tmp_path,
):
    repository = SQLiteAutomationExecutionRepository(
        database_path=str(
            tmp_path / "reporting-empty.db"
        )
    )

    report = repository.report()

    assert report.total_executions == 0
    assert report.passed == 0
    assert report.failed == 0
    assert report.not_executed == 0
    assert report.error == 0
    assert report.pass_rate_percent == 0.0
    assert report.total_duration_seconds == 0.0
    assert report.average_duration_seconds == 0.0
    assert report.latest_execution_id is None
    assert report.latest_status is None
