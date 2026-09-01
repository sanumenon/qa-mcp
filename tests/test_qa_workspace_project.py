from unittest.mock import Mock

import pytest

from qa_mcp.models.schemas import QAProject
from qa_mcp.web.qa_workspace_service import (
    QAWorkspaceService,
)


def build_service():
    project_context = Mock()
    workflow = Mock()
    requirement_versioning = Mock()
    suite_versioning = Mock()

    project_context.create_project.side_effect = (
        lambda project: project
    )

    service = QAWorkspaceService(
        project_context=project_context,
        qa_suite_workflow=workflow,
        requirement_versioning_service=(
            requirement_versioning
        ),
        suite_versioning_service=(
            suite_versioning
        ),
    )

    return (
        service,
        project_context,
    )


def test_create_project_persists_project():

    (
        service,
        project_context,
    ) = build_service()

    result = service.create_project(
        project_id="customer-portal",
        name="Customer Portal QA",
        application="Customer Portal",
        environment="test",
        description="Customer portal QA project",
        metadata={
            "team": "qa",
        },
    )

    project_context.create_project.assert_called_once()

    created_project = (
        project_context
        .create_project
        .call_args
        .args[0]
    )

    assert isinstance(
        created_project,
        QAProject,
    )

    assert (
        created_project.project_id
        == "customer-portal"
    )

    assert (
        created_project.name
        == "Customer Portal QA"
    )

    assert (
        created_project.application
        == "Customer Portal"
    )

    assert (
        created_project.environment
        == "test"
    )

    assert (
        created_project.metadata["team"]
        == "qa"
    )

    assert (
        result["project_id"]
        == "customer-portal"
    )


def test_create_project_propagates_duplicate_error():

    (
        service,
        project_context,
    ) = build_service()

    project_context.create_project.side_effect = (
        ValueError(
            "Project already exists: customer-portal"
        )
    )

    with pytest.raises(
        ValueError,
        match="Project already exists",
    ):
        service.create_project(
            project_id="customer-portal",
            name="Customer Portal QA",
            application="Customer Portal",
            environment="test",
        )