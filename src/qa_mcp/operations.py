from __future__ import annotations

import argparse
import os

from qa_mcp.core.config import load_config
from qa_mcp.core.security.backup import create_database_backup, restore_database_backup


def main() -> None:
    parser = argparse.ArgumentParser(description="QA-MCP SQLite maintenance")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("backup", help="Create and verify an online SQLite backup")
    restore_parser = subparsers.add_parser("restore", help="Restore a backup while QA-MCP is stopped")
    restore_parser.add_argument("backup_path")
    args = parser.parse_args()

    config = load_config()
    database = config["database"]
    if args.operation == "backup":
        result = create_database_backup(
            database["path"], database["backup_directory"], database["backup_retention"]
        )
        print(f"Backup created and verified: {result}")
    else:
        restore_database_backup(args.backup_path, database["path"])
        os.chmod(database["path"], 0o600)
        print("Database restored and verified; restart QA-MCP to resume service.")


if __name__ == "__main__":
    main()
