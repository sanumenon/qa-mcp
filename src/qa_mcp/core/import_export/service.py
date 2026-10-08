from __future__ import annotations

import json

from qa_mcp.infrastructure.project_repository import (
    ProjectRepository,
)

from qa_mcp.infrastructure.versioning.repositories import (
    RequirementVersionRepository,
    SuiteVersionRepository,
)

from qa_mcp.models.schemas import (
    QAProject,
    QAProjectExport,
)


class QAImportExportService:

    EXPORT_VERSION = "1.0"

    def __init__(
        self,
        project_repository: ProjectRepository,
        requirement_repository: RequirementVersionRepository,
        suite_repository: SuiteVersionRepository,
        authorization=None,
    ):
        self.project_repository = (
            project_repository
        )

        self.requirement_repository = (
            requirement_repository
        )

        self.suite_repository = (
            suite_repository
        )
        self.authorization = authorization

    def export_project(
        self,
        project_id: str,
    ) -> str:

        if self.authorization is not None:
            self.authorization.require_project(project_id)

        project = (
            self.project_repository.get(
                project_id
            )
        )

        if project is None:
            raise ValueError(
                f"Project not found: {project_id}"
            )

        requirement_versions = (
            self.requirement_repository
            .list_for_project(project_id)
        )

        suite_versions = (
            self.suite_repository
            .list_for_project(project_id)
        )

        artifact = QAProjectExport(
            export_version=self.EXPORT_VERSION,
            project=project,
            requirement_versions=(
                requirement_versions
            ),
            suite_versions=(
                suite_versions
            ),
        )

        return json.dumps(
            artifact.model_dump(),
            indent=2,
        )

    def import_project(
        self,
        payload: str,
    ) -> QAProject:

        try:

            data = json.loads(
                payload
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "Invalid QA export JSON"
            ) from exc

        try:

            artifact = (
                QAProjectExport.model_validate(
                    data
                )
            )

        except Exception as exc:

            raise ValueError(
                "Invalid QA export structure"
            ) from exc

        project = artifact.project

        # -------------------------------------------------
        # Duplicate project protection
        # -------------------------------------------------

        if self.project_repository.exists(
            project.project_id
        ):

            raise ValueError(
                f"Project already exists: "
                f"{project.project_id}"
            )

        # -------------------------------------------------
        # Validate requirement relationships
        # -------------------------------------------------

        for requirement in (
            artifact.requirement_versions
        ):

            if (
                requirement.project_id
                != project.project_id
            ):

                raise ValueError(
                    "Requirement version belongs "
                    "to a different project"
                )

        # -------------------------------------------------
        # Validate suite relationships
        # -------------------------------------------------

        requirement_ids = {
            requirement.version_id
            for requirement in (
                artifact.requirement_versions
            )
        }

        for suite in artifact.suite_versions:

            if (
                suite.project_id
                != project.project_id
            ):

                raise ValueError(
                    "Suite version belongs "
                    "to a different project"
                )

            if (
                suite.requirement_version_id
                not in requirement_ids
            ):

                raise ValueError(
                    "Suite version references "
                    "an unknown requirement version"
                )

        # -------------------------------------------------
        # Persist project
        # -------------------------------------------------

        self.project_repository.create(
            project
        )
        if self.authorization is not None:
            from qa_mcp.core.security.actor import current_actor

            self.authorization.repository.grant_project_member(
                project.project_id, current_actor().subject
            )

        # -------------------------------------------------
        # Persist requirement versions
        # -------------------------------------------------

        for requirement in (
            artifact.requirement_versions
        ):

            self.requirement_repository.create(
                requirement
            )

        # -------------------------------------------------
        # Persist suite versions
        # -------------------------------------------------

        for suite in artifact.suite_versions:

            self.suite_repository.create(
                suite
            )

        return project
