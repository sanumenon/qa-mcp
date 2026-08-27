import pytest

from qa_mcp.core.automation.execution_config import (
    AutomationExecutionConfig,
)
from qa_mcp.core.automation.execution_runner import (
    ExecutionProcessResult,
)
from qa_mcp.core.automation.execution_service import (
    AutomationExecutionService,
)
from qa_mcp.models.schemas import (
    GeneratedAutomationArtifact,
)


class FakeRunner:
    def __init__(
        self,
        result: ExecutionProcessResult,
    ):
        self.result = result
        self.command = None
        self.cwd = None
        self.timeout_seconds = None

    def run(
        self,
        command,
        cwd,
        timeout_seconds,
    ):
        self.command = command
        self.cwd = cwd
        self.timeout_seconds = timeout_seconds
        return self.result


def build_artifact(**overrides):
    data = {
        "id": "GA001",
        "automation_case_id": "AC001",
        "framework": "Playwright",
        "language": "Python",
        "file_name": "test_successful_login.py",
        "code": (
            "def test_successful_login(page):\n"
            "    pass\n"
        ),
    }

    data.update(overrides)

    return GeneratedAutomationArtifact(**data)


def test_execution_runs_generated_artifact(tmp_path):

    runner = FakeRunner(
        ExecutionProcessResult(
            exit_code=0,
            stdout="1 passed",
            stderr="",
            duration_seconds=1.25,
        )
    )

    service = AutomationExecutionService(
        config=AutomationExecutionConfig(
            timeout_seconds=30,
            workspace_root=str(tmp_path),
        ),
        runner=runner,
    )

    result = service.execute(
        build_artifact()
    )

    assert result.execution_id == "EX001"
    assert result.automation_artifact_id == "GA001"
    assert result.automation_case_id == "AC001"
    assert result.status == "PASSED"
    assert result.exit_code == 0
    assert result.stdout == "1 passed"
    assert result.stderr == ""
    assert result.duration_seconds == 1.25
    assert result.error is None

    assert runner.command == [
        "python",
        "-m",
        "pytest",
        "test_successful_login.py",
    ]

    assert runner.timeout_seconds == 30

    assert not (
        tmp_path / "test_successful_login.py"
    ).exists()


def test_execution_returns_failed_status(tmp_path):

    runner = FakeRunner(
        ExecutionProcessResult(
            exit_code=1,
            stdout="",
            stderr="1 failed",
            duration_seconds=2.0,
        )
    )

    service = AutomationExecutionService(
        config=AutomationExecutionConfig(
            workspace_root=str(tmp_path)
        ),
        runner=runner,
    )

    result = service.execute(
        build_artifact()
    )

    assert result.status == "FAILED"
    assert result.exit_code == 1
    assert result.stderr == "1 failed"


def test_execution_returns_timeout_status(tmp_path):

    runner = FakeRunner(
        ExecutionProcessResult(
            exit_code=None,
            stdout="",
            stderr="",
            duration_seconds=60.0,
            timed_out=True,
            error="Automation execution timed out after 60 seconds",
        )
    )

    service = AutomationExecutionService(
        config=AutomationExecutionConfig(
            timeout_seconds=60,
            workspace_root=str(tmp_path),
        ),
        runner=runner,
    )

    result = service.execute(
        build_artifact()
    )

    assert result.status == "TIMEOUT"
    assert result.exit_code is None
    assert result.error is not None
    assert "timed out" in result.error


def test_execution_returns_error_status(tmp_path):

    runner = FakeRunner(
        ExecutionProcessResult(
            exit_code=None,
            stdout="",
            stderr="",
            duration_seconds=0.1,
            error="Execution command failed",
        )
    )

    service = AutomationExecutionService(
        config=AutomationExecutionConfig(
            workspace_root=str(tmp_path)
        ),
        runner=runner,
    )

    result = service.execute(
        build_artifact()
    )

    assert result.status == "ERROR"
    assert result.exit_code is None
    assert result.error == "Execution command failed"


def test_empty_code_fails_execution():

    service = AutomationExecutionService()

    with pytest.raises(
        ValueError,
        match="Automation artifact must contain code",
    ):
        service.execute(
            build_artifact(code="")
        )


def test_missing_framework_fails_execution():

    service = AutomationExecutionService()

    with pytest.raises(
        ValueError,
        match="Automation artifact must specify a framework",
    ):
        service.execute(
            build_artifact(framework="")
        )


def test_unsupported_framework_fails_execution():

    service = AutomationExecutionService()

    with pytest.raises(
        ValueError,
        match="Unsupported automation framework",
    ):
        service.execute(
            build_artifact(
                framework="Cypress"
            )
        )