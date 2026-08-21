import uuid

from qa_mcp.server import (
    create_requirement_version,
    get_requirement_version,
    list_requirement_versions,
    create_suite_version,
    get_suite_version,
    list_suite_versions,
)


def unique_project_id(
    prefix: str,
) -> str:
    return (
        f"{prefix}-"
        f"{uuid.uuid4().hex}"
    )

def test_requirement_version_mcp_tools():

    project_id = unique_project_id(
                "mcp-version-test"
                )

    first = create_requirement_version(
        project_id=project_id,
        requirement="User can reset password.",
        application="Customer Portal",
        environment="QA",
    )

    assert first["version"] == 1

    version_id = first["version_id"]

    retrieved = get_requirement_version(
        version_id
    )

    assert retrieved["version_id"] == (
        version_id
    )

    assert retrieved["requirement"] == (
        "User can reset password."
    )

    versions = list_requirement_versions(
        project_id
    )

    assert len(versions) == 1
    assert versions[0]["version"] == 1


def test_requirement_versions_increment():

    project_id = unique_project_id(
                "mcp-version-increment"
            )

    first = create_requirement_version(
        project_id=project_id,
        requirement="Requirement V1",
        application="Customer Portal",
        environment="QA",
    )

    second = create_requirement_version(
        project_id=project_id,
        requirement="Requirement V2",
        application="Customer Portal",
        environment="QA",
    )

    assert first["version"] == 1
    assert second["version"] == 2


def sample_test_cases():

    return {
        "test_cases": [
            {
                "id": "TC001",
                "title": "Reset password",
                "priority": "High",
                "test_type": "Functional",
                "preconditions": [
                    "User has a registered account."
                ],
                "steps": [
                    "Open login page.",
                    "Select Forgot Password.",
                    "Enter registered email.",
                    "Submit request.",
                ],
                "expected_result": (
                    "Password reset instructions "
                    "are sent."
                ),
            }
        ]
    }


def sample_review():

    return {
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


def test_suite_version_mcp_tools():

    project_id = unique_project_id(
        "mcp-suite-test"
    )

    requirement = create_requirement_version(
        project_id=project_id,
        requirement="User can reset password.",
        application="Customer Portal",
        environment="QA",
    )

    result = create_suite_version(
        project_id=project_id,
        requirement_version_id=(
            requirement["version_id"]
        ),
        test_cases=sample_test_cases(),
        review=sample_review(),
    )

    assert result["version"] == 1

    suite_id = result["suite_id"]

    assert result[
        "requirement_version_id"
    ] == requirement["version_id"]

    retrieved = get_suite_version(
        suite_id
    )

    assert retrieved["suite_id"] == suite_id

    assert retrieved[
        "requirement_version_id"
    ] == requirement["version_id"]

    suites = list_suite_versions(
        project_id
    )

    assert len(suites) == 1

    assert suites[0]["version"] == 1