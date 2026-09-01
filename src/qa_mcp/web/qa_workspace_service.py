from __future__ import annotations

from qa_mcp.core.project.context import ProjectContext
from qa_mcp.core.versioning.service import (
    QARequirementVersioningService,
    QASuiteVersioningService,
)
from qa_mcp.models.schemas import (
    QAProject,
    QASuiteResult,
    RequirementRequest,
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
    ):
        self.project_context = project_context
        self.qa_suite_workflow = qa_suite_workflow
        self.requirement_versioning_service = (
            requirement_versioning_service
        )
        self.suite_versioning_service = (
            suite_versioning_service
        )

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

    def generate_qa_suite(
        self,
        project_id: str,
        requirement: str,
    ) -> dict:
        """Generate and persist a complete QA suite."""

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

        suite_version = (
            self.suite_versioning_service
            .create_suite_version(
                project_id=project.project_id,
                requirement_version_id=(
                    requirement_version.version_id
                ),
                test_cases=result.test_cases,
                review=result.review,
            )
        )

        return {
            "project": project.model_dump(),
            "requirement_version": (
                requirement_version.model_dump()
            ),
            "suite_version": (
                suite_version.model_dump()
            ),
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