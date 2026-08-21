from __future__ import annotations

from abc import ABC, abstractmethod

from qa_mcp.models.schemas import (
    QARequirementVersion,
    QASuiteVersion,
)


class RequirementVersionRepository(ABC):

    @abstractmethod
    def create(
        self,
        requirement: QARequirementVersion,
    ) -> QARequirementVersion:
        ...

    @abstractmethod
    def get(
        self,
        version_id: str,
    ) -> QARequirementVersion | None:
        ...

    @abstractmethod
    def list_for_project(
        self,
        project_id: str,
    ) -> list[QARequirementVersion]:
        ...


class SuiteVersionRepository(ABC):

    @abstractmethod
    def create(
        self,
        suite: QASuiteVersion,
    ) -> QASuiteVersion:
        ...

    @abstractmethod
    def get(
        self,
        suite_id: str,
    ) -> QASuiteVersion | None:
        ...

    @abstractmethod
    def list_for_project(
        self,
        project_id: str,
    ) -> list[QASuiteVersion]:
        ...