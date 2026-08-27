import subprocess
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionProcessResult:
    """Raw result returned by the controlled subprocess runner."""

    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False
    error: str | None = None


class AutomationExecutionRunner:
    """Run automation commands through a controlled subprocess boundary."""

    def run(
        self,
        command: list[str],
        cwd: str,
        timeout_seconds: int,
    ) -> ExecutionProcessResult:
        """Execute a command and capture its result."""

        started_at = time.monotonic()

        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )

            duration = time.monotonic() - started_at

            return ExecutionProcessResult(
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                duration_seconds=duration,
            )

        except subprocess.TimeoutExpired as exc:
            duration = time.monotonic() - started_at

            stdout = (
                exc.stdout
                if isinstance(exc.stdout, str)
                else ""
            )

            stderr = (
                exc.stderr
                if isinstance(exc.stderr, str)
                else ""
            )

            return ExecutionProcessResult(
                exit_code=None,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=duration,
                timed_out=True,
                error=(
                    "Automation execution timed out "
                    f"after {timeout_seconds} seconds"
                ),
            )

        except OSError as exc:
            duration = time.monotonic() - started_at

            return ExecutionProcessResult(
                exit_code=None,
                stdout="",
                stderr="",
                duration_seconds=duration,
                error=str(exc),
            )