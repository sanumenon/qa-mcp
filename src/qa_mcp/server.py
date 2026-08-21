from mcp.server.fastmcp import FastMCP

from qa_mcp.core.config import load_config
from qa_mcp.core.llm import create_llm

from qa_mcp.models.schemas import (
    RequirementRequest,
    TestCaseGenerationRequest,
    TestCaseResponse,
)

from qa_mcp.tools.requirement.analyzer import (
    RequirementAnalyzer,
)

from qa_mcp.tools.testcase.generator import (
    TestCaseGenerator,
)

from qa_mcp.tools.testcase.reviewer import (
    TestCaseReviewer,
)

from qa_mcp.tools.workflow.qa_suite import (
    QASuiteWorkflow,
)

from qa_mcp.models.schemas import (
    QAProject,
    RequirementRequest,
    TestCaseGenerationRequest,
    TestCaseResponse,
)

from qa_mcp.core.project.context import ProjectContext

from qa_mcp.infrastructure.sqlite_project_repository import (
    SQLiteProjectRepository,
)

from qa_mcp.infrastructure.versioning.sqlite_version_repository import (
    SQLiteRequirementVersionRepository,
    SQLiteSuiteVersionRepository,
)

from qa_mcp.core.versioning.service import (
    QARequirementVersioningService,
    QASuiteVersioningService,
)

from qa_mcp.core.import_export.service import (
    QAImportExportService,
)

from qa_mcp.infrastructure.versioning.sqlite_version_repository import (
    SQLiteRequirementVersionRepository,
    SQLiteSuiteVersionRepository,
)

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

config = load_config()


# ---------------------------------------------------------
# LLM
# ---------------------------------------------------------

llm = create_llm(config)


# ---------------------------------------------------------
# QA Services
# ---------------------------------------------------------

requirement_analyzer = RequirementAnalyzer(
    llm
)

testcase_generator = TestCaseGenerator(
    llm
)

testcase_reviewer = TestCaseReviewer(
    llm
)

qa_suite_workflow = QASuiteWorkflow(
    llm
)

project_repository = SQLiteProjectRepository()

project_context = ProjectContext(
    project_repository
)

requirement_version_repository = (
    SQLiteRequirementVersionRepository()
)

suite_version_repository = (
    SQLiteSuiteVersionRepository()
)

import_export_service = QAImportExportService(
    project_repository=project_repository,
    requirement_repository=(
        requirement_version_repository
    ),
    suite_repository=(
        suite_version_repository
    ),
)

requirement_version_repository = (
    SQLiteRequirementVersionRepository()
)

suite_version_repository = (
    SQLiteSuiteVersionRepository()
)

requirement_versioning_service = (
    QARequirementVersioningService(
        requirement_version_repository
    )
)

suite_versioning_service = (
    QASuiteVersioningService(
        suite_version_repository
    )
)


# ---------------------------------------------------------
# MCP Server
# ---------------------------------------------------------

mcp = FastMCP(
    config["application"]["name"]
)


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@mcp.tool()
def health() -> dict:
    """Return the current server status."""

    return {
        "status": "ok",
        "application": config["application"]["name"],
        "environment": config["application"]["environment"],
    }


# ---------------------------------------------------------
# LLM Test
# ---------------------------------------------------------

@mcp.tool()
def test_llm(
    prompt: str,
) -> dict:
    """Send a prompt through the configured LLM provider."""

    response = llm.generate(
        prompt
    )

    return {
        "provider": config["llm"]["provider"],
        "response": response,
    }


# ---------------------------------------------------------
# Requirement Analyzer
# ---------------------------------------------------------

@mcp.tool()
def analyze_requirement(
    requirement: str,
    application: str = "Unknown",
) -> dict:
    """Analyze a software requirement for QA test design."""

    request = RequirementRequest(
        requirement=requirement,
        application=application,
    )

    analysis = (
        requirement_analyzer.analyze(
            request
        )
    )

    return analysis.model_dump()


# ---------------------------------------------------------
# Test Case Generator
# ---------------------------------------------------------

@mcp.tool()
def generate_test_cases(
    requirement: str,
    application: str = "Unknown",
) -> dict:
    """Generate structured test cases."""

    requirement_request = (
        RequirementRequest(
            requirement=requirement,
            application=application,
        )
    )

    analysis = (
        requirement_analyzer.analyze(
            requirement_request
        )
    )

    generation_request = (
        TestCaseGenerationRequest(
            requirement=requirement_request,
            analysis=analysis,
        )
    )

    result = (
        testcase_generator.generate(
            generation_request
        )
    )

    return result.model_dump()


# ---------------------------------------------------------
# Test Case Reviewer
# ---------------------------------------------------------

@mcp.tool()
def review_test_cases(
    requirement: str,
    test_cases: dict,
    application: str = "Unknown",
) -> dict:
    """Review generated test cases."""

    requirement_request = (
        RequirementRequest(
            requirement=requirement,
            application=application,
        )
    )

    analysis = (
        requirement_analyzer.analyze(
            requirement_request
        )
    )

    test_case_response = (
        TestCaseResponse.model_validate(
            test_cases
        )
    )

    review = (
        testcase_reviewer.review(
            requirement=requirement_request,
            analysis=analysis,
            test_cases=test_case_response,
        )
    )

    return review.model_dump()


# ---------------------------------------------------------
# Complete QA Suite
# ---------------------------------------------------------

@mcp.tool()
def generate_qa_suite(
    requirement: str,
    application: str = "Unknown",
) -> dict:
    """
    Analyze a requirement, generate test cases,
    review the test cases, and return the complete
    QA suite.
    """

    request = RequirementRequest(
        requirement=requirement,
        application=application,
    )

    result = (
        qa_suite_workflow.run(
            request
        )
    )

    return result.model_dump()


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

# ---------------------------------------------------------
# QA Project Context
# ---------------------------------------------------------

@mcp.tool()
def create_qa_project(
    project_id: str,
    name: str,
    application: str,
    environment: str,
    description: str = "",
    metadata: dict[str, str] | None = None,
) -> dict:
    """Create a QA project in the current project context."""

    project = QAProject(
        project_id=project_id,
        name=name,
        description=description,
        application=application,
        environment=environment,
        metadata=metadata or {},
    )

    result = project_context.create_project(
        project
    )

    return result.model_dump()


@mcp.tool()
def get_qa_project(
    project_id: str,
) -> dict:
    """Retrieve a QA project from the current project context."""

    project = project_context.get_project(
        project_id
    )

    return project.model_dump()

# ---------------------------------------------------------
# QA Requirement Versioning
# ---------------------------------------------------------

@mcp.tool()
def create_requirement_version(
    project_id: str,
    requirement: str,
    application: str,
    environment: str,
) -> dict:
    """Create a new immutable requirement version."""

    result = (
        requirement_versioning_service
        .create_requirement_version(
            project_id=project_id,
            requirement=requirement,
            application=application,
            environment=environment,
        )
    )

    return result.model_dump()


@mcp.tool()
def get_requirement_version(
    version_id: str,
) -> dict:
    """Retrieve a requirement version."""

    result = (
        requirement_versioning_service
        .get_requirement_version(
            version_id
        )
    )

    return result.model_dump()


@mcp.tool()
def list_requirement_versions(
    project_id: str,
) -> list[dict]:
    """List all requirement versions for a project."""

    results = (
        requirement_versioning_service
        .list_requirement_versions(
            project_id
        )
    )

    return [
        item.model_dump()
        for item in results
    ]
# ---------------------------------------------------------
# QA Suite Versioning
# ---------------------------------------------------------

@mcp.tool()
def create_suite_version(
    project_id: str,
    requirement_version_id: str,
    test_cases: dict,
    review: dict,
) -> dict:
    """Create a new immutable QA suite version."""

    test_case_response = (
        TestCaseResponse.model_validate(
            test_cases
        )
    )

    # TestCaseReview is the structured Pydantic
    # representation of the review generated
    # by the reviewer.
    from qa_mcp.models.schemas import TestCaseReview

    review_response = (
        TestCaseReview.model_validate(
            review
        )
    )

    result = (
        suite_versioning_service
        .create_suite_version(
            project_id=project_id,
            requirement_version_id=(
                requirement_version_id
            ),
            test_cases=test_case_response,
            review=review_response,
        )
    )

    return result.model_dump()


@mcp.tool()
def get_suite_version(
    suite_id: str,
) -> dict:
    """Retrieve a QA suite version."""

    result = (
        suite_versioning_service
        .get_suite_version(
            suite_id
        )
    )

    return result.model_dump()


@mcp.tool()
def list_suite_versions(
    project_id: str,
) -> list[dict]:
    """List all QA suite versions for a project."""

    results = (
        suite_versioning_service
        .list_suite_versions(
            project_id
        )
    )

    return [
        item.model_dump()
        for item in results
    ]

# ---------------------------------------------------------
# QA Project Import / Export
# ---------------------------------------------------------

@mcp.tool()
def export_qa_project(
    project_id: str,
) -> dict:
    """Export a persisted QA project and its versioned QA artifacts."""

    payload = (
        import_export_service.export_project(
            project_id
        )
    )

    return {
        "project_id": project_id,
        "export_version": "1.0",
        "payload": payload,
    }


@mcp.tool()
def import_qa_project(
    payload: str,
) -> dict:
    """Import a QA project and its versioned QA artifacts."""

    project = (
        import_export_service.import_project(
            payload
        )
    )

    return project.model_dump()

if __name__ == "__main__":
    mcp.run()