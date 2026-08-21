from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from qa_mcp.models.schemas import QAProject

from qa_mcp.infrastructure.project_repository import (
    ProjectRepository,
)


class SQLiteProjectRepository(
    ProjectRepository
):

    def __init__(
        self,
        database_path: str = "data/qa_mcp.db",
    ):
        self.database_path = Path(
            database_path
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    def _connect(
        self,
    ) -> sqlite3.Connection:

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        return connection

    def _initialize_database(
        self,
    ) -> None:

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS qa_projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    application TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )

            connection.commit()

    def create(
        self,
        project: QAProject,
    ) -> QAProject:

        if self.exists(
            project.project_id
        ):
            raise ValueError(
                f"Project already exists: "
                f"{project.project_id}"
            )

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO qa_projects (
                    project_id,
                    name,
                    description,
                    application,
                    environment,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    project.project_id,
                    project.name,
                    project.description,
                    project.application,
                    project.environment,
                    json.dumps(
                        project.metadata
                    ),
                ),
            )

            connection.commit()

        return project

    def get(
        self,
        project_id: str,
    ) -> QAProject | None:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT
                    project_id,
                    name,
                    description,
                    application,
                    environment,
                    metadata
                FROM qa_projects
                WHERE project_id = ?
                """,
                (project_id,),
            ).fetchone()

        if row is None:
            return None

        return QAProject(
            project_id=row["project_id"],
            name=row["name"],
            description=row["description"],
            application=row["application"],
            environment=row["environment"],
            metadata=json.loads(
                row["metadata"]
            ),
        )

    def exists(
        self,
        project_id: str,
    ) -> bool:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT 1
                FROM qa_projects
                WHERE project_id = ?
                LIMIT 1
                """,
                (project_id,),
            ).fetchone()

        return row is not None