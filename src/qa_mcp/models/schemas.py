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
    metadata: dict[str, str] = {}

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