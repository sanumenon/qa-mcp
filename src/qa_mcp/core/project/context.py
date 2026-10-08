from __future__ import annotations

from qa_mcp.infrastructure.project_repository import (
    ProjectRepository,
)

from qa_mcp.models.schemas import QAProject


class ProjectContext:

    def __init__(
        self,
        repository: ProjectRepository,
        authorization=None,
    ):
        self.repository = repository
        self.authorization = authorization

    def create_project(
        self,
        project: QAProject,
    ) -> QAProject:

        if self.repository.exists(
            project.project_id
        ):
            raise ValueError(
                f"Project already exists: "
                f"{project.project_id}"
            )

        result = self.repository.create(
            project
        )
        if self.authorization is not None:
            from qa_mcp.core.security.actor import current_actor

            self.authorization.repository.grant_project_member(
                project.project_id, current_actor().subject
            )
        return result

    def list_projects(
        self,
    ) -> list[QAProject]:
        if self.authorization is None:
            return self.repository.list()
        visible = self.authorization.visible_project_ids()
        if visible is None:
            return self.repository.list()
        return [
            project
            for project_id in visible
            if (project := self.repository.get(project_id)) is not None
        ]

    def get_project(
        self,
        project_id: str,
    ) -> QAProject:

        if self.authorization is not None:
            self.authorization.require_project(project_id)

        project = self.repository.get(
            project_id
        )

        if project is None:
            raise ValueError(
                f"Project not found: "
                f"{project_id}"
            )

        return project
