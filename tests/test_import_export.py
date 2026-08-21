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

from qa_mcp.models.schemas import (
    QAProject,
    QARequirementVersion,
    QASuiteVersion,
    TestCaseResponse,
    TestCaseReview as Review,
)


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

    return (
        service,
        project_repository,
        requirement_repository,
        suite_repository,
    )


def sample_project():

    return QAProject(
        project_id="export-test",
        name="Export Test Project",
        description="Import/export test",
        application="Customer Portal",
        environment="QA",
        metadata={
            "owner": "QA Team"
        },
    )


def sample_requirement():

    return QARequirementVersion(
        version_id="req-v1",
        project_id="export-test",
        version=1,
        requirement=(
            "User can reset password."
        ),
        application="Customer Portal",
        environment="QA",
        created_at=(
            "2026-08-21T00:00:00+00:00"
        ),
    )


def sample_test_cases():

    return TestCaseResponse.model_validate(
        {
            "test_cases": [
                {
                    "id": "TC001",
                    "title": "Reset password",
                    "priority": "High",
                    "test_type": "Functional",
                    "preconditions": [],
                    "steps": [
                        "Open login page.",
                        "Select Forgot Password.",
                    ],
                    "expected_result": (
                        "Reset instructions are sent."
                    ),
                }
            ]
        }
    )


def sample_review():

    return Review.model_validate(
        {
            "overall_quality": "Good",
            "coverage_score": 85,
            "duplicate_test_cases": [],
            "missing_scenarios": [],
            "weak_test_cases": [],
            "requirement_gaps": [],
            "priority_issues": [],
            "recommendations": [],
            "summary": "Good coverage.",
        }
    )


def sample_suite():

    return QASuiteVersion(
        suite_id="suite-v1",
        project_id="export-test",
        requirement_version_id="req-v1",
        version=1,
        test_cases=sample_test_cases(),
        review=sample_review(),
        created_at=(
            "2026-08-21T00:00:00+00:00"
        ),
    )


def seed_project(
    project_repository,
    requirement_repository,
    suite_repository,
):

    project_repository.create(
        sample_project()
    )

    requirement_repository.create(
        sample_requirement()
    )

    suite_repository.create(
        sample_suite()
    )


def test_export_from_persisted_data(
    tmp_path,
):

    (
        service,
        project_repository,
        requirement_repository,
        suite_repository,
    ) = create_service(
        tmp_path
    )

    seed_project(
        project_repository,
        requirement_repository,
        suite_repository,
    )

    payload = service.export_project(
        "export-test"
    )

    data = json.loads(
        payload
    )

    assert (
        data["project"]["project_id"]
        == "export-test"
    )

    assert len(
        data["requirement_versions"]
    ) == 1

    assert len(
        data["suite_versions"]
    ) == 1


def test_import_persists_project_and_versions(
    tmp_path,
):

    (
        service,
        project_repository,
        requirement_repository,
        suite_repository,
    ) = create_service(
        tmp_path
    )

    # Build a portable artifact directly for
    # the import test.
    artifact = {
        "export_version": "1.0",
        "project": sample_project().model_dump(),
        "requirement_versions": [
            sample_requirement().model_dump()
        ],
        "suite_versions": [
            sample_suite().model_dump()
        ],
    }

    payload = json.dumps(
        artifact
    )

    result = service.import_project(
        payload
    )

    assert (
        result.project_id
        == "export-test"
    )

    persisted_project = (
        project_repository.get(
            "export-test"
        )
    )

    assert persisted_project is not None

    persisted_requirements = (
        requirement_repository
        .list_for_project(
            "export-test"
        )
    )

    assert len(
        persisted_requirements
    ) == 1

    persisted_suites = (
        suite_repository
        .list_for_project(
            "export-test"
        )
    )

    assert len(
        persisted_suites
    ) == 1

    assert (
        persisted_suites[0]
        .requirement_version_id
        == "req-v1"
    )


def test_import_rejects_duplicate_project(
    tmp_path,
):

    (
        service,
        project_repository,
        _,
        _,
    ) = create_service(
        tmp_path
    )

    project_repository.create(
        sample_project()
    )

    payload = json.dumps(
        {
            "export_version": "1.0",
            "project": sample_project().model_dump(),
            "requirement_versions": [],
            "suite_versions": [],
        }
    )

    with pytest.raises(
        ValueError,
        match="Project already exists",
    ):

        service.import_project(
            payload
        )


def test_import_rejects_cross_project_requirement(
    tmp_path,
):

    service, _, _, _ = create_service(
        tmp_path
    )

    requirement = (
        sample_requirement()
    )

    requirement.project_id = (
        "different-project"
    )

    payload = json.dumps(
        {
            "export_version": "1.0",
            "project": sample_project().model_dump(),
            "requirement_versions": [
                requirement.model_dump()
            ],
            "suite_versions": [],
        }
    )

    with pytest.raises(
        ValueError,
        match=(
            "Requirement version belongs "
            "to a different project"
        ),
    ):

        service.import_project(
            payload
        )


def test_import_rejects_unknown_requirement_reference(
    tmp_path,
):

    service, _, _, _ = create_service(
        tmp_path
    )

    suite = sample_suite()

    suite.requirement_version_id = (
        "does-not-exist"
    )

    payload = json.dumps(
        {
            "export_version": "1.0",
            "project": sample_project().model_dump(),
            "requirement_versions": [
                sample_requirement().model_dump()
            ],
            "suite_versions": [
                suite.model_dump()
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match=(
            "unknown requirement version"
        ),
    ):

        service.import_project(
            payload
        )


def test_import_rejects_cross_project_suite(
    tmp_path,
):

    service, _, _, _ = create_service(
        tmp_path
    )

    suite = sample_suite()

    suite.project_id = (
        "different-project"
    )

    payload = json.dumps(
        {
            "export_version": "1.0",
            "project": sample_project().model_dump(),
            "requirement_versions": [
                sample_requirement().model_dump()
            ],
            "suite_versions": [
                suite.model_dump()
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match=(
            "Suite version belongs "
            "to a different project"
        ),
    ):

        service.import_project(
            payload
        )

def test_export_import_round_trip(
    tmp_path,
):

    # ---------------------------------------------
    # Database A
    # ---------------------------------------------

    (
        source_service,
        source_project_repository,
        source_requirement_repository,
        source_suite_repository,
    ) = create_service(
        tmp_path / "source"
    )

    seed_project(
        source_project_repository,
        source_requirement_repository,
        source_suite_repository,
    )

    exported = (
        source_service.export_project(
            "export-test"
        )
    )

    # ---------------------------------------------
    # Database B
    # ---------------------------------------------

    (
        target_service,
        target_project_repository,
        target_requirement_repository,
        target_suite_repository,
    ) = create_service(
        tmp_path / "target"
    )

    imported_project = (
        target_service.import_project(
            exported
        )
    )

    # ---------------------------------------------
    # Verify project
    # ---------------------------------------------

    assert (
        imported_project.project_id
        == "export-test"
    )

    persisted_project = (
        target_project_repository.get(
            "export-test"
        )
    )

    assert persisted_project is not None

    assert (
        persisted_project.name
        == "Export Test Project"
    )

    assert (
        persisted_project.application
        == "Customer Portal"
    )

    # ---------------------------------------------
    # Verify requirement versions
    # ---------------------------------------------

    requirements = (
        target_requirement_repository
        .list_for_project(
            "export-test"
        )
    )

    assert len(requirements) == 1

    assert (
        requirements[0].version
        == 1
    )

    assert (
        requirements[0].version_id
        == "req-v1"
    )

    # ---------------------------------------------
    # Verify suite versions
    # ---------------------------------------------

    suites = (
        target_suite_repository
        .list_for_project(
            "export-test"
        )
    )

    assert len(suites) == 1

    assert (
        suites[0].version
        == 1
    )

    # ---------------------------------------------
    # Verify relationship
    # ---------------------------------------------

    assert (
        suites[0].requirement_version_id
        == requirements[0].version_id
    )