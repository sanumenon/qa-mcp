from mcp.server.fastmcp import FastMCP

from qa_mcp.core.config import load_config
from qa_mcp.core.llm import create_llm

from pydantic import ValidationError

from qa_mcp.core.jira.factory import (
    create_jira_service,
)

from qa_mcp.core.github.factory import (
    create_github_service,
)

from qa_mcp.core.slack.factory import (
    create_slack_service,
)

from qa_mcp.core.automation.candidate_selector import (
    AutomationCandidateSelector,
)

from qa_mcp.core.automation.candidate_service import (
    AutomationCandidateService,
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

from qa_mcp.core.automation.service import (
    AutomationService,
)

from qa_mcp.tools.automation.generator import (
    AutomationCaseGenerator,
)

from qa_mcp.core.automation.code_generation_service import (
    AutomationCodeGenerationService,
)

from qa_mcp.core.automation.execution_service import (
    AutomationExecutionService,
)
from qa_mcp.core.automation.execution_history_service import (
    AutomationExecutionHistoryService,
)

from qa_mcp.core.automation.execution_reporting_service import (
    AutomationExecutionReportingService,
)
from qa_mcp.core.automation.execution_failure_analysis_service import (
    AutomationExecutionFailureAnalysisService,
)

from qa_mcp.tools.workflow.qa_suite import (
    QASuiteWorkflow,
)

from qa_mcp.models.schemas import (
    QAProject,
    RequirementRequest,
    TestCase,
    TestCaseGenerationRequest,
    TestCaseResponse,
    AutomationCase,
    GeneratedAutomationArtifact,
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

from qa_mcp.core.automation.candidate_generation_service import (
    AutomationCandidateGenerationService,
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

jira_service = create_jira_service(
    config
)

slack_service = create_slack_service(
    config
)

github_service = create_github_service(
    config
)

automation_case_generator = AutomationCaseGenerator(
    llm
)

automation_service = AutomationService(
    automation_case_generator
)

automation_candidate_service = (
    AutomationCandidateService(
        AutomationCandidateSelector()
    )
)

automation_candidate_generation_service = (
    AutomationCandidateGenerationService(
        candidate_service=automation_candidate_service,
        automation_service=automation_service,
    )
)

automation_code_generation_service = (
    AutomationCodeGenerationService()
)

automation_execution_service = (
    AutomationExecutionService()
)

automation_execution_history_service = (
    AutomationExecutionHistoryService()
)

automation_execution_reporting_service = (
    AutomationExecutionReportingService(
        automation_execution_history_service
    )
)
automation_execution_failure_analysis_service = (
    AutomationExecutionFailureAnalysisService()
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
# Jira
# ---------------------------------------------------------

@mcp.tool()
def get_jira_issue(
    issue_key: str,
) -> dict:
    """Retrieve a Jira issue by key."""

    if jira_service is None:
        raise ValueError(
            "Jira connector is not configured"
        )

    result = jira_service.get_issue(
        issue_key
    )

    return result.model_dump()


@mcp.tool()
def search_jira_issues(
    jql: str,
    max_results: int = 50,
) -> dict:
    """Search Jira issues using JQL."""

    if jira_service is None:
        raise ValueError(
            "Jira connector is not configured"
        )

    result = jira_service.search_issues(
        jql=jql,
        max_results=max_results,
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

# ---------------------------------------------------------
# GitHub Read-Only Operations
# ---------------------------------------------------------

@mcp.tool()
def get_github_repository(
    owner: str,
    repository: str,
) -> dict:
    """Retrieve a GitHub repository."""

    if github_service is None:
        raise RuntimeError(
            "GitHub connector is not configured"
        )

    result = (
        github_service.get_repository(
            owner=owner,
            repository=repository,
        )
    )

    return result.model_dump()


@mcp.tool()
def get_github_issue(
    owner: str,
    repository: str,
    issue_number: int,
) -> dict:
    """Retrieve a GitHub issue."""

    if github_service is None:
        raise RuntimeError(
            "GitHub connector is not configured"
        )

    result = (
        github_service.get_issue(
            owner=owner,
            repository=repository,
            issue_number=issue_number,
        )
    )

    return result.model_dump()


@mcp.tool()
def get_github_pull_request(
    owner: str,
    repository: str,
    pull_number: int,
) -> dict:
    """Retrieve a GitHub pull request."""

    if github_service is None:
        raise RuntimeError(
            "GitHub connector is not configured"
        )

    result = (
        github_service.get_pull_request(
            owner=owner,
            repository=repository,
            pull_number=pull_number,
        )
    )

    return result.model_dump()


@mcp.tool()
def search_github_issues(
    query: str,
    max_results: int = 50,
) -> list[dict]:
    """Search GitHub issues."""

    if github_service is None:
        raise RuntimeError(
            "GitHub connector is not configured"
        )

    results = (
        github_service.search_issues(
            query=query,
            max_results=max_results,
        )
    )

    return [
        item.model_dump()
        for item in results
    ]

@mcp.tool()
def get_slack_channel(
    channel: str,
) -> dict:
    """Retrieve a Slack channel."""

    if slack_service is None:
        raise RuntimeError(
            "Slack connector is not configured"
        )

    result = slack_service.get_channel(
        channel
    )

    return result.model_dump()


@mcp.tool()
def get_slack_messages(
    channel: str,
    limit: int = 50,
) -> list[dict]:
    """Retrieve recent Slack messages."""

    if slack_service is None:
        raise RuntimeError(
            "Slack connector is not configured"
        )

    results = slack_service.get_messages(
        channel,
        limit=limit,
    )

    return [
        item.model_dump()
        for item in results
    ]


@mcp.tool()
def search_slack_messages(
    query: str,
    max_results: int = 50,
) -> dict:
    """Search Slack messages."""

    if slack_service is None:
        raise RuntimeError(
            "Slack connector is not configured"
        )

    result = slack_service.search_messages(
        query,
        max_results=max_results,
    )

    return result.model_dump()


@mcp.tool()
def get_slack_thread(
    channel: str,
    thread_ts: str,
) -> dict:
    """Retrieve a Slack message thread."""

    if slack_service is None:
        raise RuntimeError(
            "Slack connector is not configured"
        )

    result = slack_service.get_thread(
        channel,
        thread_ts,
    )

    return result.model_dump()

@mcp.tool()
def generate_automation(
    test_case: dict,
) -> dict:
    """Generate automation candidates for a test case."""

    try:
        qa_test_case = TestCase(
            **test_case
        )
    except Exception as exc:
        raise ValueError(
            "Invalid test case"
        ) from exc

    result = automation_service.generate_automation(
        qa_test_case
    )

    return result.model_dump()

@mcp.tool()
def select_automation_candidates(
    test_cases: list[dict],
) -> dict:
    """Select test cases suitable for automation."""

    try:
        qa_test_cases = [
            TestCase(
                **test_case
            )
            for test_case in test_cases
        ]

        result = (
            automation_candidate_service.select_candidates(
                qa_test_cases
            )
        )

        return result.model_dump()

    except Exception as exc:
        raise ValueError(
            f"Invalid test cases: {exc}"
        ) from exc

@mcp.tool()
def generate_automation_for_candidates(
    test_cases: list[dict],
) -> list[dict]:
    """Select automation candidates and generate automation for them."""

    try:
        qa_test_cases = [
            TestCase(
                **test_case
            )
            for test_case in test_cases
        ]

        result = (
            automation_candidate_generation_service.generate(
                qa_test_cases
            )
        )

        return [
            automation_case.model_dump()
            for automation_case in result
        ]

    except Exception as exc:
        raise ValueError(
            f"Invalid test cases: {exc}"
        ) from exc

@mcp.tool()
def generate_automation_code(
    automation_case: dict,
) -> dict:
    """Generate executable automation code from an automation case."""

    try:
        qa_automation_case = AutomationCase(
            **automation_case
        )

        result = (
            automation_code_generation_service.generate(
                qa_automation_case
            )
        )

        return result.model_dump()

    except Exception as exc:
        raise ValueError(
            f"Invalid automation case: {exc}"
        ) from exc

@mcp.tool()
def execute_automation_code(
    artifact: dict,
) -> dict:
    """Execute a generated automation artifact."""

    try:
        generated_artifact = GeneratedAutomationArtifact(
            **artifact
        )

        result = automation_execution_service.execute(
            generated_artifact
        )

        automation_execution_history_service.save(
            result
        )

        return result.model_dump()

    except Exception as exc:
        raise ValueError(
            f"Invalid automation artifact: {exc}"
        ) from exc


@mcp.tool()
def get_automation_execution(
    execution_id: str,
) -> dict:
    """Retrieve a persisted automation execution result."""

    result = (
        automation_execution_history_service.get(
            execution_id
        )
    )

    if result is None:
        raise ValueError(
            f"Automation execution not found: {execution_id}"
        )

    return result.model_dump()



@mcp.tool()
def get_automation_execution_report(
    automation_case_id: str | None = None,
) -> dict:
    """Return an aggregated report of automation executions."""

    report = (
        automation_execution_reporting_service.report(
            automation_case_id=automation_case_id,
        )
    )

    return report.model_dump()


@mcp.tool()
def list_automation_executions(
    automation_case_id: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List persisted automation execution results."""

    results = (
        automation_execution_history_service.list(
            automation_case_id=automation_case_id,
            limit=limit,
        )
    )

    return [
        result.model_dump()
        for result in results
    ]
    
if __name__ == "__main__":
    mcp.run()

# ---------------------------------------------------------
# Automation Execution Failure Analysis
# ---------------------------------------------------------

@mcp.tool()
def analyze_automation_failures(
    automation_case_id: str | None = None,
    limit: int = 50,
) -> dict:
    """Analyze persisted automation execution failures."""

    result = automation_execution_failure_analysis_service.analyze(
        automation_case_id=automation_case_id,
        limit=limit,
    )

    return result.model_dump()
