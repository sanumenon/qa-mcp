from __future__ import annotations

from qa_mcp.infrastructure.project_repository import (
    ProjectRepository,
)

from qa_mcp.models.schemas import QAProject


class ProjectContext:

    def __init__(
        self,
        repository: ProjectRepository,
    ):
        self.repository = repository

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

        return self.repository.create(
            project
        )

    def get_project(
        self,
        project_id: str,
    ) -> QAProject:

        project = self.repository.get(
            project_id
        )

        if project is None:
            raise ValueError(
                f"Project not found: "
                f"{project_id}"
            )

        return project