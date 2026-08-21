from __future__ import annotations

import json
import sqlite3

from qa_mcp.infrastructure.versioning.repositories import (
    RequirementVersionRepository,
    SuiteVersionRepository,
)

from qa_mcp.models.schemas import (
    QARequirementVersion,
    QASuiteVersion,
)

from qa_mcp.models.schemas import (
    QARequirementVersion,
    QASuiteVersion,
    TestCaseResponse,
    TestCaseReview,
)


class SQLiteRequirementVersionRepository(
    RequirementVersionRepository
):

    def __init__(
        self,
        database_path: str = "data/qa_mcp.db",
    ):
        self.database_path = database_path
        self._initialize_database()

    def _connect(self):
        connection = sqlite3.connect(
            self.database_path
        )
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self):

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                qa_requirement_versions (
                    version_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    requirement TEXT NOT NULL,
                    application TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(project_id, version)
                )
                """
            )

            connection.commit()

    def create(
        self,
        requirement: QARequirementVersion,
    ) -> QARequirementVersion:

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO qa_requirement_versions (
                    version_id,
                    project_id,
                    version,
                    requirement,
                    application,
                    environment,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    requirement.version_id,
                    requirement.project_id,
                    requirement.version,
                    requirement.requirement,
                    requirement.application,
                    requirement.environment,
                    requirement.created_at,
                ),
            )

            connection.commit()

        return requirement

    def get(
        self,
        version_id: str,
    ) -> QARequirementVersion | None:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM qa_requirement_versions
                WHERE version_id = ?
                """,
                (version_id,),
            ).fetchone()

        if row is None:
            return None

        return QARequirementVersion(
            version_id=row["version_id"],
            project_id=row["project_id"],
            version=row["version"],
            requirement=row["requirement"],
            application=row["application"],
            environment=row["environment"],
            created_at=row["created_at"],
        )

    def list_for_project(
        self,
        project_id: str,
    ) -> list[QARequirementVersion]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM qa_requirement_versions
                WHERE project_id = ?
                ORDER BY version
                """,
                (project_id,),
            ).fetchall()

        return [
            QARequirementVersion(
                version_id=row["version_id"],
                project_id=row["project_id"],
                version=row["version"],
                requirement=row["requirement"],
                application=row["application"],
                environment=row["environment"],
                created_at=row["created_at"],
            )
            for row in rows
        ]


class SQLiteSuiteVersionRepository(
    SuiteVersionRepository
):

    def __init__(
        self,
        database_path: str = "data/qa_mcp.db",
    ):
        self.database_path = database_path
        self._initialize_database()

    def _connect(self):
        connection = sqlite3.connect(
            self.database_path
        )
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self):

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                qa_suite_versions (
                    suite_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    requirement_version_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    test_cases TEXT NOT NULL,
                    review TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(project_id, version)
                )
                """
            )

            connection.commit()

    def create(
        self,
        suite: QASuiteVersion,
    ) -> QASuiteVersion:

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO qa_suite_versions (
                    suite_id,
                    project_id,
                    requirement_version_id,
                    version,
                    test_cases,
                    review,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    suite.suite_id,
                    suite.project_id,
                    suite.requirement_version_id,
                    suite.version,
                    json.dumps(
                        suite.test_cases.model_dump()
                    ),
                    json.dumps(
                        suite.review.model_dump()
                    ),
                    suite.created_at,
                ),
            )

            connection.commit()

        return suite

    def get(
        self,
        suite_id: str,
    ) -> QASuiteVersion | None:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM qa_suite_versions
                WHERE suite_id = ?
                """,
                (suite_id,),
            ).fetchone()

        if row is None:
            return None

        return QASuiteVersion(
            suite_id=row["suite_id"],
            project_id=row["project_id"],
            requirement_version_id=(
                row["requirement_version_id"]
            ),
            version=row["version"],
            test_cases=TestCaseResponse.model_validate(
                json.loads(row["test_cases"])
            ),
            review=TestCaseReview.model_validate(
                json.loads(row["review"])
            ),
            created_at=row["created_at"],
        )

    def list_for_project(
        self,
        project_id: str,
    ) -> list[QASuiteVersion]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM qa_suite_versions
                WHERE project_id = ?
                ORDER BY version
                """,
                (project_id,),
            ).fetchall()

        return [
            QASuiteVersion(
                suite_id=row["suite_id"],
                project_id=row["project_id"],
                requirement_version_id=(
                    row["requirement_version_id"]
                ),
                version=row["version"],
                test_cases=TestCaseResponse.model_validate(
                    json.loads(row["test_cases"])
                ),
                review=TestCaseReview.model_validate(
                    json.loads(row["review"])
                ),
                created_at=row["created_at"],
            )
            for row in rows
        ]