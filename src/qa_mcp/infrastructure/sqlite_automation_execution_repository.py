from __future__ import annotations

import sqlite3
from pathlib import Path

from qa_mcp.models.schemas import AutomationExecutionResult


class SQLiteAutomationExecutionRepository:
    """Persist and retrieve automation execution history."""

    def __init__(
        self,
        database_path: str = "data/qa_mcp.db",
    ):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self._initialize_database()

    def _connect(self):
        connection = sqlite3.connect(
            str(self.database_path)
        )
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                automation_execution_history (
                    execution_id TEXT PRIMARY KEY,
                    automation_artifact_id TEXT NOT NULL,
                    automation_case_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    exit_code INTEGER,
                    stdout TEXT NOT NULL,
                    stderr TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    error TEXT
                )
                """
            )
            connection.commit()

    def save(
        self,
        result: AutomationExecutionResult,
    ) -> AutomationExecutionResult:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO
                automation_execution_history (
                    execution_id,
                    automation_artifact_id,
                    automation_case_id,
                    status,
                    exit_code,
                    stdout,
                    stderr,
                    duration_seconds,
                    error
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.execution_id,
                    result.automation_artifact_id,
                    result.automation_case_id,
                    result.status,
                    result.exit_code,
                    result.stdout,
                    result.stderr,
                    result.duration_seconds,
                    result.error,
                ),
            )
            connection.commit()

        return result

    def get(
        self,
        execution_id: str,
    ) -> AutomationExecutionResult | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM automation_execution_history
                WHERE execution_id = ?
                """,
                (execution_id,),
            ).fetchone()

        if row is None:
            return None

        return self._to_model(row)

    def list(
        self,
        automation_case_id: str | None = None,
        limit: int = 50,
    ) -> list[AutomationExecutionResult]:
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        with self._connect() as connection:
            if automation_case_id is None:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM automation_execution_history
                    ORDER BY rowid DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM automation_execution_history
                    WHERE automation_case_id = ?
                    ORDER BY rowid DESC
                    LIMIT ?
                    """,
                    (
                        automation_case_id,
                        limit,
                    ),
                ).fetchall()

        return [
            self._to_model(row)
            for row in rows
        ]

    def report(
        self,
        automation_case_id: str | None = None,
    ):
        from qa_mcp.models.execution_reporting import (
            AutomationExecutionReport,
        )

        with self._connect() as connection:
            where_clause = ""
            params = ()

            if automation_case_id is not None:
                where_clause = (
                    " WHERE automation_case_id = ?"
                )
                params = (automation_case_id,)

            summary = connection.execute(
                f'''
                SELECT
                    COUNT(*) AS total_executions,
                    SUM(
                        CASE
                            WHEN status = 'PASSED' THEN 1
                            ELSE 0
                        END
                    ) AS passed,
                    SUM(
                        CASE
                            WHEN status = 'FAILED' THEN 1
                            ELSE 0
                        END
                    ) AS failed,
                    SUM(
                        CASE
                            WHEN status = 'NOT_EXECUTED' THEN 1
                            ELSE 0
                        END
                    ) AS not_executed,
                    SUM(
                        CASE
                            WHEN status = 'ERROR' THEN 1
                            ELSE 0
                        END
                    ) AS error,
                    COALESCE(
                        SUM(duration_seconds),
                        0.0
                    ) AS total_duration_seconds,
                    COALESCE(
                        AVG(duration_seconds),
                        0.0
                    ) AS average_duration_seconds
                FROM automation_execution_history
                {where_clause}
                ''',
                params,
            ).fetchone()

            latest = connection.execute(
                f'''
                SELECT execution_id, status
                FROM automation_execution_history
                {where_clause}
                ORDER BY rowid DESC
                LIMIT 1
                ''',
                params,
            ).fetchone()

        total = summary["total_executions"] or 0
        passed = summary["passed"] or 0

        pass_rate = (
            (passed / total) * 100.0
            if total > 0
            else 0.0
        )

        return AutomationExecutionReport(
            total_executions=total,
            passed=passed,
            failed=summary["failed"] or 0,
            not_executed=summary["not_executed"] or 0,
            error=summary["error"] or 0,
            pass_rate_percent=pass_rate,
            total_duration_seconds=(
                summary["total_duration_seconds"] or 0.0
            ),
            average_duration_seconds=(
                summary["average_duration_seconds"] or 0.0
            ),
            latest_execution_id=(
                latest["execution_id"]
                if latest is not None
                else None
            ),
            latest_status=(
                latest["status"]
                if latest is not None
                else None
            ),
        )

    def analyze_failures(
        self,
        automation_case_id: str | None = None,
        limit: int = 50,
    ):
        from qa_mcp.models.execution_failure_analysis import (
            AutomationExecutionFailure,
            AutomationExecutionFailureAnalysis,
        )

        if limit < 1:
            raise ValueError("limit must be greater than zero")

        with self._connect() as connection:
            where_clause = ""
            params: tuple = ()

            if automation_case_id is not None:
                where_clause = (
                    " WHERE automation_case_id = ?"
                )
                params = (automation_case_id,)

            total_row = connection.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM automation_execution_history
                {where_clause}
                """,
                params,
            ).fetchone()

            failure_where = (
                " WHERE status IN ('FAILED', 'ERROR')"
            )

            if automation_case_id is not None:
                failure_where += (
                    " AND automation_case_id = ?"
                )

            failure_params = (
                (automation_case_id,)
                if automation_case_id is not None
                else ()
            )

            counts = connection.execute(
                f"""
                SELECT
                    SUM(
                        CASE
                            WHEN status = 'FAILED' THEN 1
                            ELSE 0
                        END
                    ) AS failed_executions,
                    SUM(
                        CASE
                            WHEN status = 'ERROR' THEN 1
                            ELSE 0
                        END
                    ) AS error_executions
                FROM automation_execution_history
                {failure_where}
                """,
                failure_params,
            ).fetchone()

            rows = connection.execute(
                f"""
                SELECT
                    execution_id,
                    automation_artifact_id,
                    automation_case_id,
                    status,
                    exit_code,
                    stdout,
                    stderr,
                    duration_seconds,
                    error
                FROM automation_execution_history
                {failure_where}
                ORDER BY rowid DESC
                LIMIT ?
                """,
                (*failure_params, limit),
            ).fetchall()

            affected_rows = connection.execute(
                f"""
                SELECT DISTINCT automation_case_id
                FROM automation_execution_history
                {failure_where}
                ORDER BY automation_case_id
                """,
                failure_params,
            ).fetchall()

        total_executions = total_row["total"] or 0
        failed_executions = counts["failed_executions"] or 0
        error_executions = counts["error_executions"] or 0
        total_failures = (
            failed_executions + error_executions
        )

        failure_rate = (
            (total_failures / total_executions) * 100.0
            if total_executions > 0
            else 0.0
        )

        failures = []

        for row in rows:
            message = (
                row["error"]
                or row["stderr"]
                or row["stdout"]
                or "Automation execution failed"
            )

            failures.append(
                AutomationExecutionFailure(
                    execution_id=row["execution_id"],
                    automation_artifact_id=(
                        row["automation_artifact_id"]
                    ),
                    automation_case_id=(
                        row["automation_case_id"]
                    ),
                    status=row["status"],
                    exit_code=row["exit_code"],
                    message=message,
                    stderr=row["stderr"],
                    duration_seconds=(
                        row["duration_seconds"]
                    ),
                )
            )

        latest_failure = failures[0] if failures else None

        return AutomationExecutionFailureAnalysis(
            total_executions=total_executions,
            failed_executions=failed_executions,
            error_executions=error_executions,
            total_failures=total_failures,
            failure_rate_percent=failure_rate,
            affected_automation_cases=[
                row["automation_case_id"]
                for row in affected_rows
            ],
            latest_failure_execution_id=(
                latest_failure.execution_id
                if latest_failure
                else None
            ),
            latest_failure_status=(
                latest_failure.status
                if latest_failure
                else None
            ),
            failures=failures,
        )

    @staticmethod
    def _to_model(row) -> AutomationExecutionResult:
        return AutomationExecutionResult(
            execution_id=row["execution_id"],
            automation_artifact_id=(
                row["automation_artifact_id"]
            ),
            automation_case_id=row["automation_case_id"],
            status=row["status"],
            exit_code=row["exit_code"],
            stdout=row["stdout"],
            stderr=row["stderr"],
            duration_seconds=row["duration_seconds"],
            error=row["error"],
        )
