from __future__ import annotations

import sqlite3
import os
from pathlib import Path
from typing import Mapping


class SQLiteAuthorizationRepository:
    """Project memberships and minimal security audit evidence."""

    def __init__(
        self,
        database_path: str = "data/qa_mcp.db",
        legacy_ownership: Mapping[str, str] | None = None,
    ):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate(legacy_ownership or {})
        if self.database_path.exists():
            os.chmod(self.database_path, 0o600)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.database_path))
        connection.row_factory = sqlite3.Row
        return connection

    def _migrate(self, legacy_ownership: Mapping[str, str]) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS qa_schema_migrations "
                "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS qa_project_memberships ("
                "project_id TEXT NOT NULL, actor_id TEXT NOT NULL, "
                "role TEXT NOT NULL CHECK(role IN ('project_member')), "
                "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, "
                "PRIMARY KEY(project_id, actor_id))"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_qa_memberships_actor "
                "ON qa_project_memberships(actor_id)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS qa_security_audit ("
                "audit_id INTEGER PRIMARY KEY AUTOINCREMENT, actor_id TEXT NOT NULL, "
                "project_id TEXT, action TEXT NOT NULL, outcome TEXT NOT NULL, "
                "timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, request_id TEXT)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_qa_audit_project_time "
                "ON qa_security_audit(project_id, timestamp)"
            )
            connection.execute(
                "INSERT OR IGNORE INTO qa_schema_migrations(version) VALUES (1)"
            )

            # Apply only explicit operator-provided mappings. Mapping is
            # idempotent and happens in the same SQLite transaction.
            for project_id, actor_id in legacy_ownership.items():
                if not project_id or not actor_id:
                    continue
                exists = connection.execute(
                    "SELECT 1 FROM qa_projects WHERE project_id = ?",
                    (project_id,),
                ).fetchone()
                if exists:
                    connection.execute(
                        "INSERT OR IGNORE INTO qa_project_memberships "
                        "(project_id, actor_id, role) VALUES (?, ?, 'project_member')",
                        (project_id, actor_id),
                    )

    def grant_project_member(self, project_id: str, actor_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO qa_project_memberships "
                "(project_id, actor_id, role) VALUES (?, ?, 'project_member')",
                (project_id, actor_id),
            )
            connection.commit()

    def revoke_project_member(self, project_id: str, actor_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM qa_project_memberships WHERE project_id = ? AND actor_id = ?",
                (project_id, actor_id),
            )
            connection.commit()
            return cursor.rowcount > 0

    def is_project_member(self, project_id: str, actor_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM qa_project_memberships WHERE project_id = ? AND actor_id = ?",
                (project_id, actor_id),
            ).fetchone()
        return row is not None

    def project_exists(self, project_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM qa_projects WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        return row is not None

    def list_project_ids(self, actor_id: str) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT project_id FROM qa_project_memberships WHERE actor_id = ? ORDER BY project_id",
                (actor_id,),
            ).fetchall()
        return [row["project_id"] for row in rows]

    def list_members(self, project_id: str) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT actor_id FROM qa_project_memberships WHERE project_id = ? ORDER BY actor_id",
                (project_id,),
            ).fetchall()
        return [row["actor_id"] for row in rows]

    def unmapped_project_ids(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT p.project_id FROM qa_projects p LEFT JOIN qa_project_memberships m "
                "ON p.project_id = m.project_id WHERE m.project_id IS NULL ORDER BY p.project_id"
            ).fetchall()
        return [row["project_id"] for row in rows]

    def record_audit(
        self,
        actor_id: str,
        project_id: str | None,
        action: str,
        outcome: str,
        request_id: str | None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO qa_security_audit "
                "(actor_id, project_id, action, outcome, request_id) VALUES (?, ?, ?, ?, ?)",
                (actor_id, project_id, action[:160], outcome[:32], request_id),
            )
            connection.commit()

    def database_ready(self) -> bool:
        try:
            with self._connect() as connection:
                connection.execute("SELECT 1").fetchone()
            return True
        except sqlite3.Error:
            return False

    def migration_version(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COALESCE(MAX(version), 0) AS version FROM qa_schema_migrations"
            ).fetchone()
        return int(row["version"])
