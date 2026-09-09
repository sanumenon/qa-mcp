from __future__ import annotations

from datetime import datetime, timezone

from qa_mcp.core.project.context import ProjectContext
from qa_mcp.core.automation.candidate_service import (
    AutomationCandidateService,
)
from qa_mcp.core.automation.candidate_generation_service import (
    AutomationCandidateGenerationService,
)
from qa_mcp.core.automation.code_generation_service import (
    AutomationCodeGenerationService,
)
from qa_mcp.core.automation.candidate_selector import (
    AutomationCandidateSelector,
)
from qa_mcp.core.versioning.service import (
    QARequirementVersioningService,
    QASuiteVersioningService,
)
from qa_mcp.infrastructure.sqlite_qa_workspace_artifact_repository import (
    SQLiteQAWorkspaceArtifactRepository,
)
from qa_mcp.models.schemas import (
    QAProject,
    QASuiteResult,
    RequirementRequest,
    TestCase,
    TestCaseResponse,
    TestCaseReview,
)
from qa_mcp.tools.workflow.qa_suite import (
    QASuiteWorkflow,
)


class QAWorkspaceService:
    """Application service for the web-based AI QA workspace."""

    def __init__(
        self,
        project_context: ProjectContext,
        qa_suite_workflow: QASuiteWorkflow,
        requirement_versioning_service: (
            QARequirementVersioningService
        ),
        suite_versioning_service: (
            QASuiteVersioningService
        ),
        automation_candidate_service: (
            AutomationCandidateService | None
        ) = None,
        automation_candidate_generation_service: (
            AutomationCandidateGenerationService | None
        ) = None,
        automation_code_generation_service: (
            AutomationCodeGenerationService | None
        ) = None,
        workspace_artifact_repository: (
            SQLiteQAWorkspaceArtifactRepository | None
        ) = None,
    ):
        self.project_context = project_context
        self.qa_suite_workflow = qa_suite_workflow

        self.requirement_versioning_service = (
            requirement_versioning_service
        )

        self.suite_versioning_service = (
            suite_versioning_service
        )

        self.automation_candidate_service = (
            automation_candidate_service
            or AutomationCandidateService(
                AutomationCandidateSelector()
            )
        )

        self.automation_candidate_generation_service = (
            automation_candidate_generation_service
        )

        self.automation_code_generation_service = (
            automation_code_generation_service
            or AutomationCodeGenerationService()
        )

        self.workspace_artifact_repository = (
            workspace_artifact_repository
            or SQLiteQAWorkspaceArtifactRepository()
        )

    def list_projects(
        self,
    ) -> list[QAProject]:
        return self.project_context.list_projects()

    def create_project(
        self,
        project_id: str,
        name: str,
        application: str,
        environment: str,
        description: str = "",
        metadata: dict[str, str] | None = None,
    ) -> dict:
        """Create and persist a QA project."""

        project = QAProject(
            project_id=project_id,
            name=name,
            description=description,
            application=application,
            environment=environment,
            metadata=metadata or {},
        )

        result = self.project_context.create_project(
            project
        )

        return result.model_dump()


    def get_project(
        self,
        project_id: str,
    ) -> QAProject:
        """Retrieve a QA project."""

        return self.project_context.get_project(
            project_id
        )

    def get_project_qa_workspace(
        self,
        project_id: str,
    ) -> dict:
        """Return persisted QA artifacts for a project."""

        project = self.get_project(
            project_id
        )

        requirement_versions = (
            self.requirement_versioning_service
            .list_requirement_versions(
                project_id
            )
        )

        suite_versions = (
            self.suite_versioning_service
            .list_suite_versions(
                project_id
            )
        )

        test_cases = []

        for suite_version in suite_versions:
            for test_case in suite_version.test_cases.test_cases:
                test_cases.append(
                    {
                        "suite_id": suite_version.suite_id,
                        "suite_version": suite_version.version,
                        "requirement_version_id": (
                            suite_version.requirement_version_id
                        ),
                        "test_case": test_case.model_dump(),
                    }
                )

        automation_artifacts = (
            self.workspace_artifact_repository
            .list_for_project(
                project_id
            )
        )

        candidate_test_cases = [
            TestCase.model_validate(
                item["test_case"]
            )
            for item in test_cases
        ]

        candidate_ids = set(
            self.automation_candidate_service
            .select_candidates(
                candidate_test_cases
            ).candidate_ids
        )

        return {
            "project": project.model_dump(),
            "requirement_versions": [
                version.model_dump()
                for version in requirement_versions
            ],
            "suite_versions": [
                version.model_dump()
                for version in suite_versions
            ],
            "test_cases": [
                {
                    **item["test_case"],
                    "suite_id": item["suite_id"],
                    "suite_version": item["suite_version"],
                    "requirement_version_id": (
                        item["requirement_version_id"]
                    ),
                    "automation_candidate": (
                        item["test_case"]["id"]
                        in candidate_ids
                    ),
                }
                for item in test_cases
            ],
            "automation_artifacts": automation_artifacts,
        }

    def generate_automation_from_project(
        self,
        project_id: str,
        selected_test_case_ids: list[str],
    ) -> dict:
        """Generate automation from persisted project test cases."""

        if not selected_test_case_ids:
            raise ValueError(
                "At least one test case must be selected"
            )

        workspace = self.get_project_qa_workspace(
            project_id
        )

        persisted_test_cases = workspace.get(
            "test_cases",
            []
        )

        test_cases_by_id = {}

        for item in persisted_test_cases:
            test_case_id = item.get("id")

            if not test_case_id:
                continue

            test_cases_by_id[test_case_id] = (
                TestCase.model_validate(item)
            )

        selected_ids = set(
            selected_test_case_ids
        )

        unknown_ids = (
            selected_ids
            - set(test_cases_by_id)
        )

        if unknown_ids:
            unknown_id = sorted(
                unknown_ids
            )[0]

            raise ValueError(
                f"Unknown test case: {unknown_id}"
            )

        selected_test_cases = [
            test_cases_by_id[test_case_id]
            for test_case_id in selected_test_case_ids
        ]

        candidate_result = (
            self.automation_candidate_service
            .select_candidates(
                selected_test_cases
            )
        )

        candidate_ids = set(
            candidate_result.candidate_ids
        )

        non_candidate_ids = [
            test_case.id
            for test_case in selected_test_cases
            if test_case.id not in candidate_ids
        ]

        if non_candidate_ids:
            raise ValueError(
                "Selected test case is not an automation candidate: "
                f"{sorted(non_candidate_ids)[0]}"
            )

        if not self.automation_candidate_generation_service:
            raise ValueError(
                "Automation candidate generation is not configured"
            )

        automation_cases = (
            self.automation_candidate_generation_service
            .generate(
                selected_test_cases
            )
        )

        test_cases_by_id = {
            test_case.id: test_case
            for test_case in selected_test_cases
        }

        automation_artifacts = []

        created_at = datetime.now(
            timezone.utc
        ).isoformat()

        for automation_case in automation_cases:
            artifact = (
                self.automation_code_generation_service
                .generate(
                    automation_case
                )
            )

            test_case_id = getattr(
                automation_case,
                "test_case_id",
                None,
            )

            if not test_case_id:
                raise ValueError(
                    "Generated automation case is missing "
                    f"test_case_id: {automation_case.id}"
                )

            if test_case_id not in test_cases_by_id:
                raise ValueError(
                    "Generated automation case references "
                    f"unknown test case: {test_case_id}"
                )

            self.workspace_artifact_repository.save(
                artifact=artifact,
                project_id=project_id,
                test_case_id=test_case_id,
                created_at=created_at,
            )

            automation_artifacts.append(
                artifact
            )

        return {
            "project": workspace["project"],
            "selected_test_case_ids": (
                selected_test_case_ids
            ),
            "automation_candidates": (
                candidate_result.model_dump()
            ),
            "automation_cases": [
                automation_case.model_dump()
                for automation_case in automation_cases
            ],
            "automation_artifacts": [
                artifact.model_dump()
                for artifact in automation_artifacts
            ],
        }

    def generate_qa_suite(
        self,
        project_id: str,
        requirement: str,
    ) -> dict:
        """Generate a QA suite preview without persisting test cases."""

        project = self.get_project(
            project_id
        )

        request = RequirementRequest(
            requirement=requirement,
            application=project.application,
        )

        result: QASuiteResult = (
            self.qa_suite_workflow.run(request)
        )

        requirement_version = (
            self.requirement_versioning_service
            .create_requirement_version(
                project_id=project.project_id,
                requirement=requirement,
                application=project.application,
                environment=project.environment,
            )
        )



        automation_candidates = (
            self.automation_candidate_service
            .select_candidates(
                result.test_cases.test_cases
            )
        )

        automation_cases = []

        if self.automation_candidate_generation_service:
            automation_cases = (
                self.automation_candidate_generation_service
                .generate(
                    result.test_cases.test_cases
                )
            )

        # Build a lookup so every generated automation artifact
        # can be associated with its originating test case.
        test_cases_by_id = {
            test_case.id: test_case
            for test_case in result.test_cases.test_cases
        }

        automation_artifacts = []

        created_at = datetime.now(
            timezone.utc
        ).isoformat()

        for automation_case in automation_cases:
            artifact = (
                self.automation_code_generation_service
                .generate(
                    automation_case
                )
            )

            test_case_id = getattr(
                automation_case,
                "test_case_id",
                None,
            )

            if not test_case_id:
                raise ValueError(
                    "Generated automation case is missing "
                    f"test_case_id: {automation_case.id}"
                )

            if test_case_id not in test_cases_by_id:
                raise ValueError(
                    "Generated automation case references "
                    f"unknown test case: {test_case_id}"
                )

            self.workspace_artifact_repository.save(
                artifact=artifact,
                project_id=project.project_id,
                test_case_id=test_case_id,
                created_at=created_at,
            )

            automation_artifacts.append(
                artifact
            )

        return {
            "project": project.model_dump(),
            "automation_candidates": (
                automation_candidates.model_dump()
            ),
            "automation_cases": [
                automation_case.model_dump()
                for automation_case in automation_cases
            ],
            "automation_artifacts": [
                artifact.model_dump()
                for artifact in automation_artifacts
            ],
            "requirement_version": (
                requirement_version.model_dump()
            ),
            "suite_version": None,
            "requirement": (
                result.requirement.model_dump()
            ),
            "analysis": (
                result.analysis.model_dump()
            ),
            "test_cases": (
                result.test_cases.model_dump()
            ),
            "review": (
                result.review.model_dump()
            ),
        }
    def save_selected_test_cases(
        self,
        project_id: str,
        requirement_version_id: str,
        test_cases: dict,
        review: dict,
        selected_test_case_ids: list[str],
    ) -> dict:
        """Persist only the selected generated test cases."""

        if not selected_test_case_ids:
            raise ValueError(
                "At least one test case must be selected"
            )

        generated_test_cases = test_cases.get(
            "test_cases",
            [],
        )

        selected_ids = set(
            selected_test_case_ids
        )

        generated_ids = {
            test_case["id"]
            for test_case in generated_test_cases
        }

        unknown_ids = (
            selected_ids - generated_ids
        )

        if unknown_ids:
            unknown_id = sorted(
                unknown_ids
            )[0]

            raise ValueError(
                f"Unknown test case: {unknown_id}"
            )

        selected_test_cases = [
            test_case
            for test_case in generated_test_cases
            if test_case["id"] in selected_ids
        ]

        selected_response = (
            TestCaseResponse.model_validate(
                {
                    "test_cases": selected_test_cases
                }
            )
        )

        review_response = (
            TestCaseReview.model_validate(
                review
            )
        )

        suite_version = (
            self.suite_versioning_service
            .create_suite_version(
                project_id=project_id,
                requirement_version_id=(
                    requirement_version_id
                ),
                test_cases=selected_response,
                review=review_response,
            )
        )

        return suite_version.model_dump()