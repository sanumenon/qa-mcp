from unittest.mock import Mock

import pytest

from qa_mcp.models.schemas import (
    QAProject,
    QASuiteResult,
    RequirementAnalysis,
    RequirementRequest,
    TestCaseResponse,
)

from qa_mcp.models import schemas

from qa_mcp.web.qa_workspace_service import (
    QAWorkspaceService,
)


def build_project():
    return QAProject(
        project_id="qa-project",
        name="QA Project",
        application="Customer Portal",
        environment="test",
    )


def build_result():
    requirement = RequirementRequest(
        requirement="User can reset password.",
        application="Customer Portal",
    )

    analysis = RequirementAnalysis(
        summary="Password reset workflow.",
        actors=["User"],
        functional_requirements=[
            "User can request password reset."
        ],
        business_rules=[],
        preconditions=[],
        main_workflows=[
            "Request reset",
            "Set new password",
        ],
        positive_scenarios=[
            "Valid reset request"
        ],
        negative_scenarios=[
            "Invalid reset token"
        ],
        edge_cases=[
            "Expired reset token"
        ],
        missing_information=[],
        recommended_test_types=[
            "Functional"
        ],
    )

    test_cases = TestCaseResponse(
        test_cases=[
            schemas.TestCase(
                id="TC-001",
                title="Reset password",
                priority="High",
                test_type="Functional",
                preconditions=[],
                steps=[
                    "Request password reset"
                ],
                expected_result=(
                    "Password reset succeeds"
                ),
            )
        ]
    )

    review = schemas.TestCaseReview(
        overall_quality="Good",
        coverage_score=90,
        duplicate_test_cases=[],
        missing_scenarios=[],
        weak_test_cases=[],
        requirement_gaps=[],
        priority_issues=[],
        recommendations=[
            "Add security validation."
        ],
        summary="Good coverage.",
    )

    return QASuiteResult(
        requirement=requirement,
        analysis=analysis,
        test_cases=test_cases,
        review=review,
    )


def build_service():
    project_context = Mock()
    workflow = Mock()
    requirement_versioning = Mock()
    suite_versioning = Mock()
    automation_candidate_generation_service = Mock()
    automation_code_generation_service = Mock()
    workspace_artifact_repository = Mock()

    project_context.get_project.return_value = (
        build_project()
    )

    automation_case = Mock(
        model_dump=lambda: {
            "test_case_id": "TC-001",
            "automation_type": "playwright",
        }
    )

    automation_case.id = "AC-001"
    automation_case.test_case_id = "TC-001"

    automation_candidate_generation_service.generate.return_value = [
        automation_case
    ]

    automation_artifact = Mock(
        model_dump=lambda: {
            "id": "GA001",
            "automation_case_id": "TC-001",
            "framework": "Playwright",
            "language": "Python",
            "file_name": "test_reset_password.py",
            "code": (
                "from playwright.sync_api "
                "import Page, expect"
            ),
        }
    )

    automation_artifact.id = "GA001"
    automation_artifact.automation_case_id = "TC-001"
    automation_artifact.framework = "Playwright"
    automation_artifact.language = "Python"
    automation_artifact.file_name = (
        "test_reset_password.py"
    )
    automation_artifact.code = (
        "from playwright.sync_api import Page, expect"
    )

    automation_code_generation_service.generate.return_value = (
        automation_artifact
    )

    workflow.run.return_value = build_result()

    requirement_versioning_result = Mock()
    requirement_versioning_result.version_id = (
        "REQ-001"
    )
    requirement_versioning_result.model_dump.return_value = {
        "version_id": "REQ-001",
        "project_id": "qa-project",
        "version": 1,
    }

    suite_versioning_result = Mock()
    suite_versioning_result.model_dump.return_value = {
        "suite_id": "SUITE-001",
        "project_id": "qa-project",
        "version": 1,
    }

    requirement_versioning.create_requirement_version.return_value = (
        requirement_versioning_result
    )

    suite_versioning.create_suite_version.return_value = (
        suite_versioning_result
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
        automation_candidate_generation_service=(
            automation_candidate_generation_service
        ),
        automation_code_generation_service=(
            automation_code_generation_service
        ),
        workspace_artifact_repository=(
            workspace_artifact_repository
        ),
    )

    return (
        service,
        project_context,
        workflow,
        requirement_versioning,
        suite_versioning,
        automation_candidate_generation_service,
        automation_code_generation_service,
        workspace_artifact_repository,
    )


def test_generate_qa_suite_runs_complete_workflow():
    (
        service,
        project_context,
        workflow,
        requirement_versioning,
        suite_versioning,
        automation_candidate_generation_service,
        automation_code_generation_service,
        workspace_artifact_repository,
    ) = build_service()

    result = service.generate_qa_suite(
        project_id="qa-project",
        requirement="User can reset password.",
    )

    project_context.get_project.assert_called_once_with(
        "qa-project"
    )

    workflow.run.assert_called_once()

    requirement_versioning.create_requirement_version.assert_called_once_with(
        project_id="qa-project",
        requirement=(
            "User can reset password."
        ),
        application="Customer Portal",
        environment="test",
    )

    suite_versioning.create_suite_version.assert_called_once()

    assert (
        result["project"]["project_id"]
        == "qa-project"
    )

    assert (
        result["requirement_version"]["version_id"]
        == "REQ-001"
    )

    assert (
        result["suite_version"]["suite_id"]
        == "SUITE-001"
    )

    assert result["analysis"]["summary"] == (
        "Password reset workflow."
    )

    assert (
        len(result["test_cases"]["test_cases"])
        == 1
    )

    assert result["review"]["coverage_score"] == 90

    assert result["automation_candidates"] == {
        "candidate_ids": ["TC-001"],
        "manual_ids": [],
        "total": 1,
    }

    automation_candidate_generation_service.generate.assert_called_once_with(
        build_result().test_cases.test_cases
    )

    assert result["automation_cases"] == [
        {
            "test_case_id": "TC-001",
            "automation_type": "playwright",
        }
    ]

    automation_code_generation_service.generate.assert_called_once_with(
        automation_candidate_generation_service.generate.return_value[0]
    )

    assert result["automation_artifacts"] == [
        {
            "id": "GA001",
            "automation_case_id": "TC-001",
            "framework": "Playwright",
            "language": "Python",
            "file_name": "test_reset_password.py",
            "code": (
                "from playwright.sync_api "
                "import Page, expect"
            ),
        }
    ]

    workspace_artifact_repository.save.assert_called_once()

    save_call = (
        workspace_artifact_repository
        .save.call_args.kwargs
    )

    assert save_call["project_id"] == (
        "qa-project"
    )

    assert save_call["test_case_id"] == (
        "TC-001"
    )

    assert save_call["artifact"].id == "GA001"

    assert (
        save_call["artifact"].automation_case_id
        == "TC-001"
    )

    assert (
        save_call["artifact"].framework
        == "Playwright"
    )

    assert (
        save_call["artifact"].language
        == "Python"
    )

    assert (
        save_call["artifact"].file_name
        == "test_reset_password.py"
    )

    assert save_call["artifact"].code == (
        "from playwright.sync_api "
        "import Page, expect"
    )

    assert save_call["created_at"]


def test_workspace_service_has_automation_generation_service():
    (
        service,
        project_context,
        workflow,
        requirement_versioning,
        suite_versioning,
        automation_candidate_generation_service,
        automation_code_generation_service,
        workspace_artifact_repository,
    ) = build_service()

    assert (
        service.automation_candidate_generation_service
        is automation_candidate_generation_service
    )

    assert (
        service.automation_code_generation_service
        is automation_code_generation_service
    )

    assert (
        service.workspace_artifact_repository
        is workspace_artifact_repository
    )


def test_generate_qa_suite_raises_for_unknown_project():
    (
        service,
        project_context,
        workflow,
        requirement_versioning,
        suite_versioning,
        automation_candidate_generation_service,
        automation_code_generation_service,
        workspace_artifact_repository,
    ) = build_service()

    project_context.get_project.side_effect = (
        ValueError(
            "Project not found: missing"
        )
    )

    with pytest.raises(
        ValueError,
        match="Project not found: missing",
    ):
        service.generate_qa_suite(
            project_id="missing",
            requirement="User can reset password.",
        )

    workflow.run.assert_not_called()

    requirement_versioning.create_requirement_version.assert_not_called()

    suite_versioning.create_suite_version.assert_not_called()

    workspace_artifact_repository.save.assert_not_called()


def test_generate_qa_suite_rejects_automation_case_without_test_case_id():
    (
        service,
        project_context,
        workflow,
        requirement_versioning,
        suite_versioning,
        automation_candidate_generation_service,
        automation_code_generation_service,
        workspace_artifact_repository,
    ) = build_service()

    automation_case = Mock(
        spec=["id", "model_dump"]
    )

    automation_case.id = "AC-001"

    automation_case.model_dump.return_value = {
        "automation_type": "playwright",
    }

    automation_candidate_generation_service.generate.return_value = [
        automation_case
    ]

    with pytest.raises(
        ValueError,
        match="missing test_case_id",
    ):
        service.generate_qa_suite(
            project_id="qa-project",
            requirement="User can reset password.",
        )

    automation_code_generation_service.generate.assert_called_once_with(
        automation_case
    )

    workspace_artifact_repository.save.assert_not_called()


def test_generate_qa_suite_rejects_unknown_test_case_reference():
    (
        service,
        project_context,
        workflow,
        requirement_versioning,
        suite_versioning,
        automation_candidate_generation_service,
        automation_code_generation_service,
        workspace_artifact_repository,
    ) = build_service()

    automation_case = Mock(
        spec=["id", "test_case_id", "model_dump"]
    )

    automation_case.id = "AC-001"
    automation_case.test_case_id = "TC-UNKNOWN"

    automation_case.model_dump.return_value = {
        "test_case_id": "TC-UNKNOWN",
        "automation_type": "playwright",
    }

    automation_candidate_generation_service.generate.return_value = [
        automation_case
    ]

    with pytest.raises(
        ValueError,
        match="unknown test case: TC-UNKNOWN",
    ):
        service.generate_qa_suite(
            project_id="qa-project",
            requirement="User can reset password.",
        )

    automation_code_generation_service.generate.assert_called_once_with(
        automation_case
    )

    workspace_artifact_repository.save.assert_not_called()
