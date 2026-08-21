from qa_mcp.core.versioning.service import (
    QASuiteVersioningService,
)

from qa_mcp.infrastructure.versioning.sqlite_version_repository import (
    SQLiteSuiteVersionRepository,
)

from qa_mcp.models.schemas import (
    TestCaseResponse,
    TestCaseReview as Review,
)


def create_service(
    tmp_path,
):

    repository = SQLiteSuiteVersionRepository(
        str(
            tmp_path / "qa_mcp.db"
        )
    )

    return QASuiteVersioningService(
        repository
    )


def sample_test_cases():

    return TestCaseResponse.model_validate(
        {
            "test_cases": [
                {
                    "id": "TC001",
                    "title": (
                        "Reset password "
                        "with registered email"
                    ),
                    "priority": "High",
                    "test_type": "Functional",
                    "preconditions": [
                        "User has a registered account."
                    ],
                    "steps": [
                        "Open the login page.",
                        "Select Forgot Password.",
                        "Enter the registered email.",
                        "Submit the request.",
                    ],
                    "expected_result": (
                        "Password reset instructions "
                        "are sent."
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
            "recommendations": [
                "Add additional boundary coverage."
            ],
            "summary": (
                "Good baseline coverage."
            ),
        }
    )


def test_first_suite_version_is_v1(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    result = service.create_suite_version(
        project_id="project-1",
        requirement_version_id="req-v1",
        test_cases=sample_test_cases(),
        review=sample_review(),
    )

    assert result.version == 1
    assert result.project_id == "project-1"
    assert result.requirement_version_id == (
        "req-v1"
    )


def test_second_suite_version_is_v2(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    first = service.create_suite_version(
        project_id="project-1",
        requirement_version_id="req-v1",
        test_cases=sample_test_cases(),
        review=sample_review(),
    )

    second = service.create_suite_version(
        project_id="project-1",
        requirement_version_id="req-v2",
        test_cases=sample_test_cases(),
        review=sample_review(),
    )

    assert first.version == 1
    assert second.version == 2


def test_different_project_starts_at_v1(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    service.create_suite_version(
        project_id="project-1",
        requirement_version_id="req-v1",
        test_cases=sample_test_cases(),
        review=sample_review(),
    )

    result = service.create_suite_version(
        project_id="project-2",
        requirement_version_id="req-v1",
        test_cases=sample_test_cases(),
        review=sample_review(),
    )

    assert result.version == 1
    assert result.project_id == "project-2"


def test_get_suite_version(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    created = service.create_suite_version(
        project_id="project-1",
        requirement_version_id="req-v1",
        test_cases=sample_test_cases(),
        review=sample_review(),
    )

    result = service.get_suite_version(
        created.suite_id
    )

    assert result == created


def test_list_suite_versions(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    service.create_suite_version(
        project_id="project-1",
        requirement_version_id="req-v1",
        test_cases=sample_test_cases(),
        review=sample_review(),
    )

    service.create_suite_version(
        project_id="project-1",
        requirement_version_id="req-v2",
        test_cases=sample_test_cases(),
        review=sample_review(),
    )

    service.create_suite_version(
        project_id="project-1",
        requirement_version_id="req-v3",
        test_cases=sample_test_cases(),
        review=sample_review(),
    )

    result = service.list_suite_versions(
        "project-1"
    )

    assert len(result) == 3

    assert [
        item.version
        for item in result
    ] == [1, 2, 3]


def test_missing_suite_version_is_rejected(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    try:

        service.get_suite_version(
            "does-not-exist"
        )

        assert False

    except ValueError as exc:

        assert (
            "Suite version not found"
            in str(exc)
        )


def test_suite_preserves_requirement_version(
    tmp_path,
):

    service = create_service(
        tmp_path
    )

    result = service.create_suite_version(
        project_id="project-1",
        requirement_version_id="requirement-v2",
        test_cases=sample_test_cases(),
        review=sample_review(),
    )

    assert result.requirement_version_id == (
        "requirement-v2"
    )