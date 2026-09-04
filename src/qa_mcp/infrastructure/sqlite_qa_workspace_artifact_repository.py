from __future__ import annotations

import sqlite3
from pathlib import Path

from qa_mcp.models.schemas import GeneratedAutomationArtifact


class SQLiteQAWorkspaceArtifactRepository:
    """Persist generated automation artifacts for QA workspace traceability."""

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
                qa_workspace_automation_artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    automation_case_id TEXT NOT NULL,
                    test_case_id TEXT NOT NULL,
                    framework TEXT NOT NULL,
                    language TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_workspace_artifacts_project
                ON qa_workspace_automation_artifacts(project_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_workspace_artifacts_case
                ON qa_workspace_automation_artifacts(automation_case_id)
                """
            )

            connection.commit()

    def save(
        self,
        artifact: GeneratedAutomationArtifact,
        project_id: str,
        test_case_id: str,
        created_at: str,
    ) -> GeneratedAutomationArtifact:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO
                qa_workspace_automation_artifacts (
                    artifact_id,
                    project_id,
                    automation_case_id,
                    test_case_id,
                    framework,
                    language,
                    file_name,
                    code,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact.id,
                    project_id,
                    artifact.automation_case_id,
                    test_case_id,
                    artifact.framework,
                    artifact.language,
                    artifact.file_name,
                    artifact.code,
                    created_at,
                ),
            )

            connection.commit()

        return artifact

    def get(
        self,
        artifact_id: str,
    ) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM qa_workspace_automation_artifacts
                WHERE artifact_id = ?
                """,
                (artifact_id,),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def get_for_project(
        self,
        project_id: str,
        artifact_id: str,
    ) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM qa_workspace_automation_artifacts
                WHERE project_id = ?
                  AND artifact_id = ?
                """,
                (
                    project_id,
                    artifact_id,
                ),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def list_for_project(
        self,
        project_id: str,
        limit: int = 50,
    ) -> list[dict]:
        if limit < 1:
            raise ValueError(
                "limit must be greater than zero"
            )

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM qa_workspace_automation_artifacts
                WHERE project_id = ?
                ORDER BY rowid DESC
                LIMIT ?
                """,
                (
                    project_id,
                    limit,
                ),
            ).fetchall()

        return [dict(row) for row in rows]