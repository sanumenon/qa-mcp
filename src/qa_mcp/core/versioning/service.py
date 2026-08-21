from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from qa_mcp.infrastructure.versioning.repositories import (
    RequirementVersionRepository,
    SuiteVersionRepository,
)

from qa_mcp.models.schemas import (
    QARequirementVersion,
    QASuiteVersion,
    TestCaseResponse,
    TestCaseReview,
)


class QARequirementVersioningService:

    def __init__(
        self,
        repository: RequirementVersionRepository,
    ):
        self.repository = repository

    def create_requirement_version(
        self,
        project_id: str,
        requirement: str,
        application: str,
        environment: str,
    ) -> QARequirementVersion:

        versions = (
            self.repository.list_for_project(
                project_id
            )
        )

        next_version = len(versions) + 1

        result = QARequirementVersion(
            version_id=str(uuid4()),
            project_id=project_id,
            version=next_version,
            requirement=requirement,
            application=application,
            environment=environment,
            created_at=(
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
        )

        return self.repository.create(
            result
        )

    def get_requirement_version(
        self,
        version_id: str,
    ) -> QARequirementVersion:

        result = self.repository.get(
            version_id
        )

        if result is None:
            raise ValueError(
                f"Requirement version not found: "
                f"{version_id}"
            )

        return result

    def list_requirement_versions(
        self,
        project_id: str,
    ) -> list[QARequirementVersion]:

        return self.repository.list_for_project(
            project_id
        )


class QASuiteVersioningService:

    def __init__(
        self,
        repository: SuiteVersionRepository,
    ):
        self.repository = repository

    def create_suite_version(
        self,
        project_id: str,
        requirement_version_id: str,
        test_cases: TestCaseResponse,
        review: TestCaseReview,
    ) -> QASuiteVersion:

        versions = (
            self.repository.list_for_project(
                project_id
            )
        )

        next_version = len(versions) + 1

        result = QASuiteVersion(
            suite_id=str(uuid4()),
            project_id=project_id,
            requirement_version_id=(
                requirement_version_id
            ),
            version=next_version,
            test_cases=test_cases,
            review=review,
            created_at=(
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
        )

        return self.repository.create(
            result
        )

    def get_suite_version(
        self,
        suite_id: str,
    ) -> QASuiteVersion:

        result = self.repository.get(
            suite_id
        )

        if result is None:
            raise ValueError(
                f"Suite version not found: "
                f"{suite_id}"
            )

        return result

    def list_suite_versions(
        self,
        project_id: str,
    ) -> list[QASuiteVersion]:

        return self.repository.list_for_project(
            project_id
        )