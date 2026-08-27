import sys
import time

from qa_mcp.core.automation.execution_runner import (
    AutomationExecutionRunner,
)


def test_runner_captures_successful_command(tmp_path):

    runner = AutomationExecutionRunner()

    result = runner.run(
        command=[
            sys.executable,
            "-c",
            "print('execution successful')",
        ],
        cwd=str(tmp_path),
        timeout_seconds=5,
    )

    assert result.exit_code == 0
    assert result.stdout.strip() == "execution successful"
    assert result.stderr == ""
    assert result.timed_out is False
    assert result.error is None
    assert result.duration_seconds >= 0


def test_runner_captures_failed_command(tmp_path):

    runner = AutomationExecutionRunner()

    result = runner.run(
        command=[
            sys.executable,
            "-c",
            "import sys; print('failure'); sys.exit(3)",
        ],
        cwd=str(tmp_path),
        timeout_seconds=5,
    )

    assert result.exit_code == 3
    assert result.stdout.strip() == "failure"
    assert result.timed_out is False
    assert result.error is None


def test_runner_handles_timeout(tmp_path):

    runner = AutomationExecutionRunner()

    started_at = time.monotonic()

    result = runner.run(
        command=[
            sys.executable,
            "-c",
            "import time; time.sleep(5)",
        ],
        cwd=str(tmp_path),
        timeout_seconds=1,
    )

    elapsed = time.monotonic() - started_at

    assert result.exit_code is None
    assert result.timed_out is True
    assert result.error is not None
    assert "timed out" in result.error
    assert elapsed < 4


def test_runner_handles_missing_command(tmp_path):

    runner = AutomationExecutionRunner()

    result = runner.run(
        command=[
            "qa-mcp-command-that-does-not-exist",
        ],
        cwd=str(tmp_path),
        timeout_seconds=5,
    )

    assert result.exit_code is None
    assert result.stdout == ""
    assert result.stderr == ""
    assert result.timed_out is False
    assert result.error is not None