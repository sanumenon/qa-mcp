from __future__ import annotations

import sqlite3
import os
from pathlib import Path

from qa_mcp.models.schemas import AutomationExecutionResult


class SQLiteAutomationExecutionRepository:
    """Persist and retrieve automation execution history."""

    def __init__(
        self,
        database_path: str | None = None,
    ):
        self.database_path = Path(
            database_path or os.getenv("QA_DATABASE_PATH", "data/qa_mcp.db")
        )
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

    def list_for_artifact_ids(
        self, artifact_ids: list[str], limit: int = 50,
        automation_case_id: str | None = None,
    ):
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        if not artifact_ids:
            return []
        placeholders = ", ".join("?" for _ in artifact_ids)
        case_clause = " AND automation_case_id = ?" if automation_case_id else ""
        params = (*artifact_ids, automation_case_id, limit) if automation_case_id else (*artifact_ids, limit)
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM automation_execution_history "
                f"WHERE automation_artifact_id IN ({placeholders}){case_clause} "
                "ORDER BY rowid DESC LIMIT ?",
                params,
            ).fetchall()
        return [self._to_model(row) for row in rows]

    def get_for_artifact_ids(self, execution_id: str, artifact_ids: list[str]):
        if not artifact_ids:
            return None
        placeholders = ", ".join("?" for _ in artifact_ids)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM automation_execution_history "
                f"WHERE execution_id = ? AND automation_artifact_id IN ({placeholders})",
                (execution_id, *artifact_ids),
            ).fetchone()
        return self._to_model(row) if row is not None else None

    def report_for_artifact_ids(
        self, artifact_ids: list[str], automation_case_id: str | None = None
    ):
        from qa_mcp.models.execution_reporting import AutomationExecutionReport

        if not artifact_ids:
            return AutomationExecutionReport(
                total_executions=0, passed=0, failed=0, not_executed=0,
                error=0, pass_rate_percent=0.0, total_duration_seconds=0.0,
                average_duration_seconds=0.0, latest_execution_id=None, latest_status=None,
            )
        placeholders = ", ".join("?" for _ in artifact_ids)
        case_clause = " AND automation_case_id = ?" if automation_case_id else ""
        params = (*artifact_ids, automation_case_id) if automation_case_id else tuple(artifact_ids)
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT execution_id, status, duration_seconds "
                "FROM automation_execution_history "
                f"WHERE automation_artifact_id IN ({placeholders}){case_clause} ORDER BY rowid DESC",
                params,
            ).fetchall()
        total = len(rows)
        passed = sum(row["status"] == "PASSED" for row in rows)
        durations = [row["duration_seconds"] for row in rows]
        counts = {status: sum(row["status"] == status for row in rows)
                  for status in ("FAILED", "NOT_EXECUTED", "ERROR")}
        return AutomationExecutionReport(
            total_executions=total,
            passed=passed,
            failed=counts["FAILED"],
            not_executed=counts["NOT_EXECUTED"],
            error=counts["ERROR"],
            pass_rate_percent=(passed / total * 100.0) if total else 0.0,
            total_duration_seconds=sum(durations),
            average_duration_seconds=(sum(durations) / total) if total else 0.0,
            latest_execution_id=rows[0]["execution_id"] if rows else None,
            latest_status=rows[0]["status"] if rows else None,
        )

    def analyze_failures_for_artifact_ids(
        self, artifact_ids: list[str], limit: int = 50,
        automation_case_id: str | None = None,
    ):
        from qa_mcp.models.execution_failure_analysis import (
            AutomationExecutionFailure,
            AutomationExecutionFailureAnalysis,
        )

        if limit < 1:
            raise ValueError("limit must be greater than zero")
        if not artifact_ids:
            return AutomationExecutionFailureAnalysis(
                total_executions=0, failed_executions=0, error_executions=0,
                total_failures=0, failure_rate_percent=0.0,
                affected_automation_cases=[], latest_failure_execution_id=None,
                latest_failure_status=None, failures=[],
            )
        placeholders = ", ".join("?" for _ in artifact_ids)
        case_clause = " AND automation_case_id = ?" if automation_case_id else ""
        params = (*artifact_ids, automation_case_id) if automation_case_id else tuple(artifact_ids)
        failure_params = (*params, limit)
        with self._connect() as connection:
            all_rows = connection.execute(
                "SELECT status FROM automation_execution_history "
                f"WHERE automation_artifact_id IN ({placeholders}){case_clause}",
                params,
            ).fetchall()
            failed_rows = connection.execute(
                "SELECT * FROM automation_execution_history "
                f"WHERE automation_artifact_id IN ({placeholders}) "
                f"AND status IN ('FAILED', 'ERROR'){case_clause} ORDER BY rowid DESC LIMIT ?",
                failure_params,
            ).fetchall()
            cases = connection.execute(
                "SELECT DISTINCT automation_case_id FROM automation_execution_history "
                f"WHERE automation_artifact_id IN ({placeholders}) "
                f"AND status IN ('FAILED', 'ERROR'){case_clause} ORDER BY automation_case_id",
                params,
            ).fetchall()
        failed_count = sum(row["status"] == "FAILED" for row in all_rows)
        error_count = sum(row["status"] == "ERROR" for row in all_rows)
        failures = [
            AutomationExecutionFailure(
                execution_id=row["execution_id"],
                automation_artifact_id=row["automation_artifact_id"],
                automation_case_id=row["automation_case_id"],
                status=row["status"],
                exit_code=row["exit_code"],
                message=row["error"] or row["stderr"] or row["stdout"] or "Automation execution failed",
                stderr=row["stderr"],
                duration_seconds=row["duration_seconds"],
            )
            for row in failed_rows
        ]
        total = len(all_rows)
        failure_total = failed_count + error_count
        return AutomationExecutionFailureAnalysis(
            total_executions=total,
            failed_executions=failed_count,
            error_executions=error_count,
            total_failures=failure_total,
            failure_rate_percent=(failure_total / total * 100.0) if total else 0.0,
            affected_automation_cases=[row["automation_case_id"] for row in cases],
            latest_failure_execution_id=failures[0].execution_id if failures else None,
            latest_failure_status=failures[0].status if failures else None,
            failures=failures,
        )
    def _project_artifact_ids(
        self,
        project_id: str,
        artifact_repository,
    ) -> list[str]:
        artifacts = artifact_repository.list_for_project(
            project_id=project_id
        )

        return [
            artifact.artifact_id
            if hasattr(artifact, "artifact_id")
            else artifact["artifact_id"]
            for artifact in artifacts
        ]

    def list_for_project(
        self,
        project_id: str,
        artifact_repository,
        limit: int = 50,
    ):
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        artifact_ids = self._project_artifact_ids(
            project_id=project_id,
            artifact_repository=artifact_repository,
        )

        if not artifact_ids:
            return []

        placeholders = ", ".join("?" for _ in artifact_ids)

        with self._connect() as connection:
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
                WHERE automation_artifact_id IN ({placeholders})
                ORDER BY rowid DESC
                LIMIT ?
                """,
                (*artifact_ids, limit),
            ).fetchall()

        return [self._to_model(row) for row in rows]

    def get_for_project(
        self,
        project_id: str,
        execution_id: str,
        artifact_repository,
    ):
        artifact_ids = self._project_artifact_ids(
            project_id=project_id,
            artifact_repository=artifact_repository,
        )

        if not artifact_ids:
            return None

        placeholders = ", ".join("?" for _ in artifact_ids)

        with self._connect() as connection:
            row = connection.execute(
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
                WHERE execution_id = ?
                  AND automation_artifact_id IN ({placeholders})
                LIMIT 1
                """,
                (execution_id, *artifact_ids),
            ).fetchone()

        return self._to_model(row) if row is not None else None

    def report_for_project(
        self,
        project_id: str,
        artifact_repository,
    ):
        artifact_ids = self._project_artifact_ids(
            project_id=project_id,
            artifact_repository=artifact_repository,
        )

        if not artifact_ids:
            from qa_mcp.models.execution_reporting import (
                AutomationExecutionReport,
            )

            return AutomationExecutionReport(
                total_executions=0,
                passed=0,
                failed=0,
                not_executed=0,
                error=0,
                pass_rate_percent=0.0,
                total_duration_seconds=0.0,
                average_duration_seconds=0.0,
                latest_execution_id=None,
                latest_status=None,
            )

        placeholders = ", ".join("?" for _ in artifact_ids)

        from qa_mcp.models.execution_reporting import (
            AutomationExecutionReport,
        )

        with self._connect() as connection:
            summary = connection.execute(
                f"""
                SELECT
                    COUNT(*) AS total_executions,
                    SUM(
                        CASE WHEN status = 'PASSED'
                        THEN 1 ELSE 0 END
                    ) AS passed,
                    SUM(
                        CASE WHEN status = 'FAILED'
                        THEN 1 ELSE 0 END
                    ) AS failed,
                    SUM(
                        CASE WHEN status = 'NOT_EXECUTED'
                        THEN 1 ELSE 0 END
                    ) AS not_executed,
                    SUM(
                        CASE WHEN status = 'ERROR'
                        THEN 1 ELSE 0 END
                    ) AS error,
                    COALESCE(SUM(duration_seconds), 0.0)
                        AS total_duration_seconds,
                    COALESCE(AVG(duration_seconds), 0.0)
                        AS average_duration_seconds
                FROM automation_execution_history
                WHERE automation_artifact_id IN ({placeholders})
                """,
                artifact_ids,
            ).fetchone()

            latest = connection.execute(
                f"""
                SELECT execution_id, status
                FROM automation_execution_history
                WHERE automation_artifact_id IN ({placeholders})
                ORDER BY rowid DESC
                LIMIT 1
                """,
                artifact_ids,
            ).fetchone()

        total = summary["total_executions"] or 0
        passed = summary["passed"] or 0

        return AutomationExecutionReport(
            total_executions=total,
            passed=passed,
            failed=summary["failed"] or 0,
            not_executed=summary["not_executed"] or 0,
            error=summary["error"] or 0,
            pass_rate_percent=(
                (passed / total) * 100.0
                if total > 0
                else 0.0
            ),
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

    def analyze_failures_for_project(
        self,
        project_id: str,
        artifact_repository,
        limit: int = 50,
    ):
        artifact_ids = self._project_artifact_ids(
            project_id=project_id,
            artifact_repository=artifact_repository,
        )

        if not artifact_ids:
            from qa_mcp.models.execution_failure_analysis import (
                AutomationExecutionFailureAnalysis,
            )

            return AutomationExecutionFailureAnalysis(
                total_executions=0,
                failed_executions=0,
                error_executions=0,
                total_failures=0,
                failure_rate_percent=0.0,
                affected_automation_cases=[],
                latest_failure_execution_id=None,
                latest_failure_status=None,
                failures=[],
            )

        placeholders = ", ".join("?" for _ in artifact_ids)

        from qa_mcp.models.execution_failure_analysis import (
            AutomationExecutionFailure,
            AutomationExecutionFailureAnalysis,
        )

        with self._connect() as connection:
            total_row = connection.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM automation_execution_history
                WHERE automation_artifact_id IN ({placeholders})
                """,
                artifact_ids,
            ).fetchone()

            failure_where = f"""
                WHERE automation_artifact_id IN ({placeholders})
                  AND status IN ('FAILED', 'ERROR')
            """

            counts = connection.execute(
                f"""
                SELECT
                    SUM(
                        CASE WHEN status = 'FAILED'
                        THEN 1 ELSE 0 END
                    ) AS failed_executions,
                    SUM(
                        CASE WHEN status = 'ERROR'
                        THEN 1 ELSE 0 END
                    ) AS error_executions
                FROM automation_execution_history
                {failure_where}
                """,
                artifact_ids,
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
                (*artifact_ids, limit),
            ).fetchall()

            affected_rows = connection.execute(
                f"""
                SELECT DISTINCT automation_case_id
                FROM automation_execution_history
                {failure_where}
                ORDER BY automation_case_id
                """,
                artifact_ids,
            ).fetchall()

        total_executions = total_row["total"] or 0
        failed_executions = counts["failed_executions"] or 0
        error_executions = counts["error_executions"] or 0
        total_failures = (
            failed_executions + error_executions
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
                    duration_seconds=row["duration_seconds"],
                )
            )

        latest_failure = failures[0] if failures else None

        return AutomationExecutionFailureAnalysis(
            total_executions=total_executions,
            failed_executions=failed_executions,
            error_executions=error_executions,
            total_failures=total_failures,
            failure_rate_percent=(
                (total_failures / total_executions) * 100.0
                if total_executions > 0
                else 0.0
            ),
            affected_automation_cases=[
                row["automation_case_id"]
                for row in affected_rows
            ],
            latest_failure_execution_id=(
                latest_failure.execution_id
                if latest_failure is not None
                else None
            ),
            latest_failure_status=(
                latest_failure.status
                if latest_failure is not None
                else None
            ),
            failures=failures,
        )
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
