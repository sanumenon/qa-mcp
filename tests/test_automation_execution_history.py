from qa_mcp.core.automation.execution_history_service import (
    AutomationExecutionHistoryService,
)
from qa_mcp.infrastructure.sqlite_automation_execution_repository import (
    SQLiteAutomationExecutionRepository,
)
from qa_mcp.models.schemas import AutomationExecutionResult


def build_result(
    execution_id: str,
    case_id: str,
    status: str = "PASSED",
):
    return AutomationExecutionResult(
        execution_id=execution_id,
        automation_artifact_id="ART-001",
        automation_case_id=case_id,
        status=status,
        exit_code=0 if status == "PASSED" else 1,
        stdout="1 passed" if status == "PASSED" else "",
        stderr="",
        duration_seconds=1.25,
        error=None,
    )


def test_execution_history_persists_and_retrieves_result(
    tmp_path,
):
    repository = SQLiteAutomationExecutionRepository(
        str(tmp_path / "history.db")
    )
    service = AutomationExecutionHistoryService(
        repository
    )

    result = build_result(
        "EX-S10-001",
        "AC-S10-001",
    )

    service.save(result)

    loaded = service.get("EX-S10-001")

    assert loaded is not None
    assert loaded.execution_id == "EX-S10-001"
    assert loaded.automation_case_id == "AC-S10-001"
    assert loaded.status == "PASSED"
    assert loaded.exit_code == 0
    assert loaded.stdout == "1 passed"
    assert loaded.duration_seconds == 1.25


def test_execution_history_lists_latest_results(
    tmp_path,
):
    repository = SQLiteAutomationExecutionRepository(
        str(tmp_path / "history.db")
    )
    service = AutomationExecutionHistoryService(
        repository
    )

    service.save(
        build_result(
            "EX-S10-001",
            "AC-S10-001",
        )
    )
    service.save(
        build_result(
            "EX-S10-002",
            "AC-S10-001",
            "FAILED",
        )
    )
    service.save(
        build_result(
            "EX-S10-003",
            "AC-S10-002",
        )
    )

    results = service.list(
        automation_case_id="AC-S10-001"
    )

    assert [
        result.execution_id
        for result in results
    ] == [
        "EX-S10-002",
        "EX-S10-001",
    ]


def test_execution_history_enforces_positive_limit(
    tmp_path,
):
    repository = SQLiteAutomationExecutionRepository(
        str(tmp_path / "history.db")
    )

    try:
        repository.list(limit=0)
    except ValueError as exc:
        assert "greater than zero" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for invalid limit"
        )


def test_execution_ids_are_unique_for_service_results(
    tmp_path,
):
    repository = SQLiteAutomationExecutionRepository(
        str(tmp_path / "history.db")
    )
    service = AutomationExecutionHistoryService(
        repository
    )

    first = build_result(
        "EX-S10-004",
        "AC-S10-003",
    )
    second = build_result(
        "EX-S10-005",
        "AC-S10-003",
    )

    service.save(first)
    service.save(second)

    results = service.list(
        automation_case_id="AC-S10-003"
    )

    assert len(results) == 2
    assert {
        result.execution_id
        for result in results
    } == {
        "EX-S10-004",
        "EX-S10-005",
    }
