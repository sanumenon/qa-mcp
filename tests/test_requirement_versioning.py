from qa_mcp.core.versioning.service import (
    QARequirementVersioningService,
)

from qa_mcp.infrastructure.versioning.sqlite_version_repository import (
    SQLiteRequirementVersionRepository,
)


def create_service(
    tmp_path,
):

    repository = SQLiteRequirementVersionRepository(
        str(
            tmp_path / "qa_mcp.db"
        )
    )

    return QARequirementVersioningService(
    repository
)


def test_first_requirement_version_is_v1(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    result = (
        service.create_requirement_version(
            project_id="project-1",
            requirement="User can reset password.",
            application="Customer Portal",
            environment="QA",
        )
    )

    assert result.version == 1
    assert result.project_id == "project-1"
    assert result.requirement == (
        "User can reset password."
    )


def test_second_requirement_version_is_v2(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    first = (
        service.create_requirement_version(
            project_id="project-1",
            requirement="User can reset password.",
            application="Customer Portal",
            environment="QA",
        )
    )

    second = (
        service.create_requirement_version(
            project_id="project-1",
            requirement=(
                "User can reset password "
                "using email verification."
            ),
            application="Customer Portal",
            environment="QA",
        )
    )

    assert first.version == 1
    assert second.version == 2


def test_different_project_starts_at_v1(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    service.create_requirement_version(
        project_id="project-1",
        requirement="Requirement A",
        application="App A",
        environment="QA",
    )

    result = (
        service.create_requirement_version(
            project_id="project-2",
            requirement="Requirement B",
            application="App B",
            environment="QA",
        )
    )

    assert result.version == 1
    assert result.project_id == "project-2"


def test_get_requirement_version(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    created = (
        service.create_requirement_version(
            project_id="project-1",
            requirement="Requirement A",
            application="Customer Portal",
            environment="QA",
        )
    )

    result = (
        service.get_requirement_version(
            created.version_id
        )
    )

    assert result == created


def test_list_requirement_versions(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    service.create_requirement_version(
        project_id="project-1",
        requirement="Requirement A",
        application="Customer Portal",
        environment="QA",
    )

    service.create_requirement_version(
        project_id="project-1",
        requirement="Requirement B",
        application="Customer Portal",
        environment="QA",
    )

    service.create_requirement_version(
        project_id="project-1",
        requirement="Requirement C",
        application="Customer Portal",
        environment="QA",
    )

    result = (
        service.list_requirement_versions(
            "project-1"
        )
    )

    assert len(result) == 3

    assert [
        item.version
        for item in result
    ] == [1, 2, 3]


def test_missing_requirement_version_is_rejected(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    try:

        service.get_requirement_version(
            "does-not-exist"
        )

        assert False

    except ValueError as exc:

        assert (
            "Requirement version not found"
            in str(exc)
        )