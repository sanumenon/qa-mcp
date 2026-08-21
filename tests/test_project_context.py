import pytest

from qa_mcp.core.project.context import (
    ProjectContext,
)

from qa_mcp.infrastructure.sqlite_project_repository import (
    SQLiteProjectRepository,
)

from qa_mcp.models.schemas import QAProject


def sample_project():

    return QAProject(
        project_id="customer-portal",
        name="Customer Portal",
        description="Customer web application",
        application="Customer Portal",
        environment="QA",
        metadata={
            "owner": "QA Team",
            "version": "1.0",
        },
    )


def create_context(
    tmp_path,
):

    repository = SQLiteProjectRepository(
        str(
            tmp_path / "qa_mcp.db"
        )
    )

    return ProjectContext(
        repository
    )


def test_create_project(
    tmp_path,
):

    context = create_context(
        tmp_path
    )

    project = sample_project()

    result = context.create_project(
        project
    )

    assert result.project_id == (
        "customer-portal"
    )

    assert result.name == (
        "Customer Portal"
    )


def test_get_project(
    tmp_path,
):

    context = create_context(
        tmp_path
    )

    project = sample_project()

    context.create_project(
        project
    )

    result = context.get_project(
        "customer-portal"
    )

    assert result == project


def test_duplicate_project_is_rejected(
    tmp_path,
):

    context = create_context(
        tmp_path
    )

    project = sample_project()

    context.create_project(
        project
    )

    with pytest.raises(
        ValueError,
        match="Project already exists",
    ):

        context.create_project(
            project
        )


def test_missing_project_is_rejected(
    tmp_path,
):

    context = create_context(
        tmp_path
    )

    with pytest.raises(
        ValueError,
        match="Project not found",
    ):

        context.get_project(
            "does-not-exist"
        )