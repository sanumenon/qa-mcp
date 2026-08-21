from qa_mcp.infrastructure.sqlite_project_repository import (
    SQLiteProjectRepository,
)

from qa_mcp.models.schemas import QAProject


def sample_project():

    return QAProject(
        project_id="persistent-project",
        name="Persistent Project",
        description="SQLite persistence test",
        application="Customer Portal",
        environment="QA",
        metadata={
            "owner": "QA Team",
        },
    )


def test_project_is_persisted(
    tmp_path,
):

    database = (
        tmp_path / "qa_mcp.db"
    )

    repository = SQLiteProjectRepository(
        str(database)
    )

    project = sample_project()

    repository.create(
        project
    )

    # Create a completely new repository
    # using the same database.
    new_repository = (
        SQLiteProjectRepository(
            str(database)
        )
    )

    result = new_repository.get(
        "persistent-project"
    )

    assert result == project


def test_project_exists(
    tmp_path,
):

    repository = SQLiteProjectRepository(
        str(
            tmp_path / "qa_mcp.db"
        )
    )

    assert not repository.exists(
        "persistent-project"
    )

    repository.create(
        sample_project()
    )

    assert repository.exists(
        "persistent-project"
    )


def test_missing_project_returns_none(
    tmp_path,
):

    repository = SQLiteProjectRepository(
        str(
            tmp_path / "qa_mcp.db"
        )
    )

    result = repository.get(
        "does-not-exist"
    )

    assert result is None