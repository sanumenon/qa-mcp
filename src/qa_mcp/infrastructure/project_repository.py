from __future__ import annotations

from abc import ABC, abstractmethod

from qa_mcp.models.schemas import QAProject


class ProjectRepository(ABC):

    @abstractmethod
    def create(
        self,
        project: QAProject,
    ) -> QAProject:
        ...

    @abstractmethod
    def get(
        self,
        project_id: str,
    ) -> QAProject | None:
        ...

    @abstractmethod
    def exists(
        self,
        project_id: str,
    ) -> bool:
        ...