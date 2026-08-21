import json
import pytest

from qa_mcp.core.import_export.service import (
    QAImportExportService,
)

from qa_mcp.infrastructure.sqlite_project_repository import (
    SQLiteProjectRepository,
)

from qa_mcp.infrastructure.versioning.sqlite_version_repository import (
    SQLiteRequirementVersionRepository,
    SQLiteSuiteVersionRepository,
)

from qa_mcp.server import (
    export_qa_project,
    import_qa_project,
)

import qa_mcp.server as server


def create_service(
    tmp_path,
):

    database_path = str(
        tmp_path / "qa_mcp.db"
    )

    project_repository = (
        SQLiteProjectRepository(
            database_path
        )
    )

    requirement_repository = (
        SQLiteRequirementVersionRepository(
            database_path
        )
    )

    suite_repository = (
        SQLiteSuiteVersionRepository(
            database_path
        )
    )

    service = QAImportExportService(
        project_repository=(
            project_repository
        ),
        requirement_repository=(
            requirement_repository
        ),
        suite_repository=(
            suite_repository
        ),
    )

    return service


def test_export_qa_project_tool_rejects_missing_project():

    with pytest.raises(
        ValueError,
        match="Project not found",
    ):

        export_qa_project(
            project_id="does-not-exist"
        )


def test_import_qa_project_tool(
    tmp_path,
):

    original_service = (
        server.import_export_service
    )

    try:

        server.import_export_service = (
            create_service(
                tmp_path
            )
        )

        payload = json.dumps(
            {
                "export_version": "1.0",
                "project": {
                    "project_id": (
                        "mcp-import-tool-test"
                    ),
                    "name": (
                        "MCP Import Test"
                    ),
                    "description": "",
                    "application": (
                        "Customer Portal"
                    ),
                    "environment": "QA",
                    "metadata": {},
                },
                "requirement_versions": [],
                "suite_versions": [],
            }
        )

        result = import_qa_project(
            payload
        )

        assert (
            result["project_id"]
            == "mcp-import-tool-test"
        )

        assert (
            result["name"]
            == "MCP Import Test"
        )

    finally:

        server.import_export_service = (
            original_service
        )