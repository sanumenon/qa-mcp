from pydantic import BaseModel, Field


class RequirementRequest(BaseModel):
    requirement: str = Field(min_length=1)
    application: str = Field(default="Unknown")


class RequirementAnalysis(BaseModel):
    summary: str
    actors: list[str]
    functional_requirements: list[str]
    business_rules: list[str]
    preconditions: list[str]
    main_workflows: list[str]
    positive_scenarios: list[str]
    negative_scenarios: list[str]
    edge_cases: list[str]
    missing_information: list[str]
    recommended_test_types: list[str]


class TestCase(BaseModel):
    id: str
    title: str
    priority: str
    test_type: str
    preconditions: list[str]
    steps: list[str]
    expected_result: str


class TestCaseResponse(BaseModel):
    __test__ = False

    test_cases: list[TestCase]


class TestCaseGenerationRequest(BaseModel):
    requirement: RequirementRequest
    analysis: RequirementAnalysis

class TestCaseReview(BaseModel):
    overall_quality: str
    coverage_score: int = Field(ge=0, le=100)
    duplicate_test_cases: list[str]
    missing_scenarios: list[str]
    weak_test_cases: list[str]
    requirement_gaps: list[str]
    priority_issues: list[str]
    recommendations: list[str]
    summary: str

class QASuiteResult(BaseModel):
    requirement: RequirementRequest
    analysis: RequirementAnalysis
    test_cases: TestCaseResponse
    review: TestCaseReview

class QAProject(BaseModel):
    project_id: str
    name: str
    description: str = ""
    application: str
    environment: str
    metadata: dict[str, str] = Field(
        default_factory=dict
    )

class QARequirementVersion(BaseModel):
    version_id: str
    project_id: str
    version: int
    requirement: str
    application: str
    environment: str
    created_at: str


class QASuiteVersion(BaseModel):
    suite_id: str
    project_id: str
    requirement_version_id: str
    version: int
    test_cases: TestCaseResponse
    review: TestCaseReview
    created_at: str

class QAProjectExport(BaseModel):
    """Portable representation of a QA project."""

    export_version: str = "1.0"

    project: QAProject

    requirement_versions: list[
        QARequirementVersion
    ] = Field(default_factory=list)

    suite_versions: list[
        QASuiteVersion
    ] = Field(default_factory=list)


class JiraIssue(BaseModel):
    """Normalized Jira issue representation."""

    key: str
    summary: str
    description: str = ""
    issue_type: str = ""
    status: str = ""
    priority: str = ""
    project_key: str = ""
    project_name: str = ""
    assignee: str = ""
    reporter: str = ""
    url: str = ""

class JiraSearchResult(BaseModel):
    """Normalized Jira search result."""

    issues: list[JiraIssue] = Field(
        default_factory=list
    )

    total: int = 0

class GitHubRepository(BaseModel):
    """Normalized GitHub repository representation."""

    full_name: str
    name: str
    owner: str
    description: str = ""
    url: str = ""
    default_branch: str = ""


class GitHubIssue(BaseModel):
    """Normalized GitHub issue representation."""

    number: int
    title: str
    state: str = ""
    body: str = ""
    url: str = ""
    repository: str = ""
    author: str = ""


class GitHubPullRequest(BaseModel):
    """Normalized GitHub pull request representation."""

    number: int
    title: str
    state: str = ""
    body: str = ""
    url: str = ""
    repository: str = ""
    author: str = ""
    head_branch: str = ""
    base_branch: str = ""

class SlackChannel(BaseModel):
    """Normalized Slack channel representation."""

    id: str
    name: str
    is_private: bool = False
    is_archived: bool = False
    url: str = ""


class SlackMessage(BaseModel):
    """Normalized Slack message representation."""

    ts: str
    text: str = ""
    user: str = ""
    channel: str = ""
    thread_ts: str = ""
    url: str = ""


class SlackSearchResult(BaseModel):
    """Normalized Slack message search result."""

    messages: list[SlackMessage] = Field(
        default_factory=list
    )

    total: int = 0


class SlackThread(BaseModel):
    """Normalized Slack thread representation."""

    channel: str
    thread_ts: str
    messages: list[SlackMessage] = Field(
        default_factory=list
    )

class AutomationCase(BaseModel):
    """Normalized automation candidate representation."""

    id: str
    test_case_id: str
    title: str
    automation_type: str = ""
    framework: str = ""
    priority: str = ""
    confidence: str = ""
    preconditions: list[str] = Field(
        default_factory=list
    )
    test_data: list[str] = Field(
        default_factory=list
    )
    steps: list[str] = Field(
        default_factory=list
    )
    assertions: list[str] = Field(
        default_factory=list
    )
    limitations: list[str] = Field(
        default_factory=list
    )


class AutomationCaseResponse(BaseModel):
    """Normalized automation case generation response."""

    automation_cases: list[AutomationCase] = Field(
        default_factory=list
    )

class AutomationCandidateResult(BaseModel):
    """Result of automation candidate selection."""

    candidate_ids: list[str] = Field(
        default_factory=list
    )

    manual_ids: list[str] = Field(
        default_factory=list
    )

    total: int = 0


class AutomationValidationResult(BaseModel):
    automation_case_id: str
    test_case_id: str
    valid: bool
    errors: list[str]
    warnings: list[str]

class GeneratedAutomationArtifact(BaseModel):
    id: str
    automation_case_id: str
    framework: str
    language: str
    file_name: str
    code: str

class AutomationExecutionResult(BaseModel):
    """Result of executing a generated automation artifact."""

    execution_id: str
    automation_artifact_id: str
    automation_case_id: str
    status: str
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0
    error: str | None = None

class QAWorkspaceExecutionTrace(BaseModel):
    """Complete QA lineage associated with a workspace execution."""

    project: QAProject
    requirement_version: QARequirementVersion
    suite_version: QASuiteVersion
    test_case: TestCase
    automation_case: AutomationCase
    artifact: GeneratedAutomationArtifact


class QAWorkspaceExecutionDetail(BaseModel):
    """Detailed execution investigation result for the QA workspace."""

    project: QAProject
    execution: AutomationExecutionResult
    trace: QAWorkspaceExecutionTrace
    failure_analysis: object | None = None

class QASuiteWorkspaceRequest(BaseModel):
    """Request to generate a QA suite for a project."""

    requirement: str = Field(min_length=1)

class QAProjectCreateRequest(BaseModel):
    """Request to create a QA project from the web workspace."""

    project_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    application: str = Field(min_length=1)
    environment: str = Field(min_length=1)
    description: str = ""
    metadata: dict[str, str] = Field(
        default_factory=dict
    )
