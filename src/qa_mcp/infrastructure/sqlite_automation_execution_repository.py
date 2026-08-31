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
