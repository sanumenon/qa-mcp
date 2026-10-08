from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def create_database_backup(
    database_path: str | Path,
    backup_directory: str | Path,
    retention: int = 14,
) -> Path:
    """Create and verify an online SQLite backup with restrictive permissions."""
    source_path = Path(database_path).resolve()
    destination_dir = Path(backup_directory).resolve()
    if retention < 1:
        raise ValueError("Backup retention must be at least one")
    if not source_path.is_file():
        raise FileNotFoundError("Configured SQLite database does not exist")

    destination_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(destination_dir, 0o700)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    final_path = destination_dir / f"qa_mcp-{stamp}.sqlite3"
    fd, temporary_name = tempfile.mkstemp(
        prefix=".qa_mcp-backup-", suffix=".sqlite3", dir=destination_dir
    )
    os.close(fd)
    temporary_path = Path(temporary_name)
    try:
        with sqlite3.connect(str(source_path)) as source:
            with sqlite3.connect(str(temporary_path)) as target:
                source.backup(target)
                result = target.execute("PRAGMA integrity_check").fetchone()
                if not result or result[0] != "ok":
                    raise sqlite3.DatabaseError("SQLite backup integrity check failed")
        os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, final_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    backups = sorted(
        destination_dir.glob("qa_mcp-*.sqlite3"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for old_backup in backups[retention:]:
        old_backup.unlink()
    return final_path


def restore_database_backup(
    backup_path: str | Path,
    database_path: str | Path,
) -> None:
    """Restore through SQLite's backup API; run with the application stopped."""
    source_path = Path(backup_path).resolve()
    destination = Path(database_path).resolve()
    if not source_path.is_file():
        raise FileNotFoundError("SQLite backup does not exist")
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary_name = tempfile.mkstemp(
        prefix=".qa_mcp-restore-", suffix=".sqlite3", dir=destination.parent
    )
    os.close(fd)
    temporary_path = Path(temporary_name)
    try:
        with sqlite3.connect(str(source_path)) as source:
            check = source.execute("PRAGMA integrity_check").fetchone()
            if not check or check[0] != "ok":
                raise sqlite3.DatabaseError("SQLite backup failed integrity verification")
            with sqlite3.connect(str(temporary_path)) as target:
                source.backup(target)
                target_check = target.execute("PRAGMA integrity_check").fetchone()
                if not target_check or target_check[0] != "ok":
                    raise sqlite3.DatabaseError("Restored database failed integrity verification")
        os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, destination)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()
