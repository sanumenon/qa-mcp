import pytest
import sys
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
    AutomationCase,
    GeneratedAutomationArtifact,
)

from qa_mcp.core.automation.code_generation_service import (
    AutomationCodeGenerationService,
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

    assert result.execution_id.startswith("EX-")
    assert len(result.execution_id) == 15

    assert result.automation_artifact_id == "GA001"
    assert result.automation_case_id == "AC001"
    assert result.status == "PASSED"
    assert result.exit_code == 0
    assert result.stdout == "1 passed"
    assert result.stderr == ""
    assert result.duration_seconds == 1.25
    assert result.error is None

    assert runner.command == [
        sys.executable,
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

def test_build_command_returns_controlled_pytest_invocation():
    service = AutomationExecutionService()

    command = service._build_command(
        build_artifact(file_name="test_login.py")
    )

    assert command == [
        sys.executable,
        "-m",
        "pytest",
        "test_login.py",
    ]


def test_build_command_rejects_unsupported_framework():
    service = AutomationExecutionService()

    with pytest.raises(
        ValueError,
        match="Unsupported automation framework",
    ):
        service._build_command(
            build_artifact(
                framework="Cypress",
                file_name="test_login.py",
            )
        )


def test_build_command_rejects_unsafe_artifact_filename():
    service = AutomationExecutionService()

    with pytest.raises(
        ValueError,
        match="Unsafe automation artifact filename",
    ):
        service._build_command(
            build_artifact(
                file_name="../outside.py",
            )
        )

def test_execution_config_rejects_zero_timeout():
    with pytest.raises(
        ValueError,
        match="positive integer",
    ):
        AutomationExecutionConfig(
            timeout_seconds=0
        )


def test_execution_config_rejects_negative_timeout():
    with pytest.raises(
        ValueError,
        match="positive integer",
    ):
        AutomationExecutionConfig(
            timeout_seconds=-1
        )


def test_execution_config_rejects_non_integer_timeout():
    with pytest.raises(
        ValueError,
        match="positive integer",
    ):
        AutomationExecutionConfig(
            timeout_seconds="60"
        )


def test_execution_config_rejects_boolean_timeout():
    with pytest.raises(
        ValueError,
        match="positive integer",
    ):
        AutomationExecutionConfig(
            timeout_seconds=True
        )


def test_execution_config_accepts_positive_timeout():
    config = AutomationExecutionConfig(
        timeout_seconds=30
    )

    assert config.timeout_seconds == 30


def test_execution_service_honors_keep_workspace(tmp_path):
    runner = FakeRunner(
        ExecutionProcessResult(
            exit_code=0,
            stdout="1 passed",
            stderr="",
            duration_seconds=1.0,
        )
    )

    service = AutomationExecutionService(
        config=AutomationExecutionConfig(
            timeout_seconds=30,
            workspace_root=str(tmp_path),
            keep_workspace=True,
        ),
        runner=runner,
    )

    result = service.execute(
        build_artifact()
    )

    assert result.status == "PASSED"

    workspace_path = tmp_path / next(
        path.name
        for path in tmp_path.iterdir()
        if path.is_dir()
    )

    assert workspace_path.exists()
    assert (
        workspace_path / "test_successful_login.py"
    ).exists()

def test_generated_automation_artifact_can_be_executed(
    tmp_path,
):
    automation_case = AutomationCase(
        id="AC001",
        test_case_id="TC001",
        title="Successful login",
        automation_type="UI",
        framework="Playwright",
        priority="High",
        confidence="High",
        preconditions=[],
        test_data=[],
        steps=[
            "goto: http://localhost:8000/login",
            "fill: #username = testuser",
            "click: #login",
        ],
        assertions=[
            "visible: #dashboard",
        ],
        limitations=[],
    )

    generator = AutomationCodeGenerationService()

    artifact = generator.generate(
        automation_case
    )

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

    result = service.execute(artifact)

    assert artifact.automation_case_id == "AC001"
    assert artifact.framework == "Playwright"
    assert artifact.file_name == "test_successful_login.py"

    assert "page.goto('http://localhost:8000/login')" in artifact.code
    assert (
        "page.locator('#username').fill('testuser')"
        in artifact.code
    )
    assert "page.locator('#login').click()" in artifact.code
    assert (
        "expect(page.locator('#dashboard')).to_be_visible()"
        in artifact.code
    )

    assert result.status == "PASSED"
    assert result.automation_artifact_id == artifact.id
    assert result.automation_case_id == "AC001"
    assert result.exit_code == 0

    assert runner.command == [
        sys.executable,
        "-m",
        "pytest",
        "test_successful_login.py",
    ]