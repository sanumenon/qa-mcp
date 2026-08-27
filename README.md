# QA MCP

QA MCP is a Model Context Protocol (MCP) server for structured
software-quality workflows.

The project is being developed incrementally toward a full-fledged
AI-powered QA platform using:

-   layered architecture
-   test-first development
-   Pydantic-based contracts
-   persistent SQLite storage
-   immutable QA versioning
-   project import/export
-   safe external connectors
-   AI-assisted QA analysis
-   automation candidate selection
-   Playwright automation generation
-   controlled automation execution
-   eventual QA-agent orchestration
-   eventual CI/CD and hosted product capabilities

> **Continuity rule:** This README is the authoritative development
> checkpoint for future QA MCP development sessions.

------------------------------------------------------------------------

# 1. Current Development Checkpoint

## Repository checkpoint

``` text
Branch:        main
Latest commit: 703cdb1 Complete automation execution foundation
Remote:        origin/main
Last committed milestone: Automation execution foundation
```

The latest committed checkpoint contains:

-   automation execution result contract
-   automation case traceability in execution results
-   automation execution MCP boundary
-   README checkpoint update

The next execution work is currently being developed as a separate
uncommitted increment.

## Current local development state

The current working tree contains the controlled execution pipeline
work:

``` text
AutomationExecutionConfig
        |
        v
AutomationWorkspace
        |
        v
AutomationExecutionRunner
        |
        v
AutomationExecutionService
        |
        v
AutomationExecutionResult
        |
        v
MCP execute_automation_code tool
```

Current local regression:

``` text
190 passed, 7 warnings
```

Focused execution tests:

``` text
16 passed, 1 warning
```

The execution-service focused suite currently passes:

``` text
7 passed
```

`git diff --check` is clean.

The execution pipeline changes are **not yet committed at this
checkpoint**.

------------------------------------------------------------------------

# 2. Product Vision

The long-term goal is not merely to expose isolated MCP tools.

QA MCP is intended to become an AI-driven QA platform where a user can
provide a requirement and the platform can progressively:

``` text
Requirement
    |
    v
Requirement Understanding
    |
    v
Scenario Analysis
    |
    v
Test Case Generation
    |
    v
Test Case Review
    |
    v
QA Suite / Version
    |
    v
Automation Candidate Selection
    |
    v
Automation Case
    |
    v
Automation Validation
    |
    v
Playwright Code Generation
    |
    v
Generated Automation Artifact
    |
    v
Controlled Execution
    |
    v
Execution Results
    |
    v
Reporting / Analysis
    |
    v
QA Agent / Orchestration
```

Eventually this should support integrations such as:

``` text
Jira
GitHub
Slack
CI/CD
Test repositories
Automation environments
Cloud execution
```

The UI/hosted product layer should be introduced after the core QA
capabilities are sufficiently stable.

------------------------------------------------------------------------

# 3. Development Rules --- MUST FOLLOW

These rules apply to every future change.

1.  **Implement one phase/sub-step at a time.**
2.  **Test first wherever practical.**
3.  Focused tests must pass before moving to the next implementation
    increment.
4.  The relevant feature test group must pass.
5.  The full regression suite must pass before closing a milestone.
6.  **Never weaken or delete tests merely to obtain green output.**
7.  Inspect existing code before modifying it.
8.  Preserve the layered architecture.
9.  Core business logic must remain independent of MCP transport.
10. Persistence must remain behind repository interfaces.
11. External integrations must remain mockable.
12. LLM providers must remain replaceable.
13. AI output must be validated before downstream use.
14. Do not commit secrets or real `.env` files.
15. Do not delete persistent databases merely to make tests pass.
16. Keep unrelated refactoring separate from feature work.
17. A major capability is not complete until its MCP/runtime path is
    verified.
18. Update this README at every verified milestone.
19. Commit only after the feature, tests, README, and checkpoint have
    been reviewed.
20. Do not recreate completed work from earlier milestones.

The recurring development sequence is:

``` text
Understand current checkpoint
        |
        v
Inspect repository
        |
        v
Write/update focused tests
        |
        v
Implement one increment
        |
        v
Focused tests green
        |
        v
Feature test group green
        |
        v
Full regression green
        |
        v
Runtime/MCP verification
        |
        v
Update README
        |
        v
Review git diff
        |
        v
Commit + push
```

------------------------------------------------------------------------

# 4. Architecture

The fundamental architecture is:

``` text
                         MCP CLIENT / AI ASSISTANT
                                  |
                                  v
                            QA MCP Server
                                  |
                                  v
                             MCP Tool Layer
                                  |
          +-----------------------+------------------------+
          |                       |                        |
          v                       v                        v
     QA Workflows          Core Services             Connectors
          |                       |                        |
          |                       |               +--------+--------+
          |                       |               |        |        |
          v                       v               Jira    GitHub   Slack
 Requirement Analyzer       Automation           |        |        |
 Test Case Generator        Execution            v        v        v
 Test Case Reviewer         Versioning          Service  Service  Service
 QA Suite Workflow          Project Context       |        |        |
 Candidate Selection                              v        v        v
 Automation Generation                         Client   Client   Client
 Automation Execution                           / \      / \      / \
                                                Mock     Mock    Mock
                                                Cloud    Cloud   Cloud
```

Layer responsibilities:

``` text
models/
    Domain and data contracts

core/
    Business/application services
    Factories
    Orchestration boundaries

infrastructure/
    Persistence
    External clients
    Concrete implementations

tools/
    QA-oriented application workflows

server.py
    MCP transport and tool registration
```

Core business logic must not become coupled to MCP transport.

------------------------------------------------------------------------

# 5. Repository Structure

Current important structure:

``` text
qa-mcp/
|
+-- config/
|   +-- settings.yaml
|
+-- src/qa_mcp/
|   +-- core/
|   |   +-- automation/
|   |   |   +-- candidate_generation_service.py
|   |   |   +-- candidate_selector.py
|   |   |   +-- candidate_service.py
|   |   |   +-- code_generation_service.py
|   |   |   +-- execution_config.py
|   |   |   +-- execution_runner.py
|   |   |   +-- execution_service.py
|   |   |   +-- workspace.py
|   |   |   +-- service.py
|   |   |   +-- validator.py
|   |   |
|   |   +-- github/
|   |   +-- jira/
|   |   +-- slack/
|   |   +-- import_export/
|   |   +-- project/
|   |   +-- versioning/
|   |   +-- config.py
|   |   +-- llm.py
|   |
|   +-- infrastructure/
|   |   +-- github/
|   |   +-- jira/
|   |   +-- slack/
|   |   +-- versioning/
|   |   +-- project repositories
|   |
|   +-- models/
|   |   +-- schemas.py
|   |
|   +-- tools/
|   |   +-- automation/
|   |   +-- requirement/
|   |   +-- testcase/
|   |   +-- workflow/
|   |
|   +-- server.py
|
+-- tests/
+-- data/
+-- README.md
+-- requirements.txt
```

------------------------------------------------------------------------

# 6. Phase 1 --- Foundation & QA Intelligence

**Status: COMPLETE**

Completed capabilities:

-   MCP server foundation
-   configuration loading
-   LLM abstraction
-   mock LLM support
-   requirement analysis
-   test-case generation
-   test-case review
-   end-to-end QA suite workflow

Core flow:

``` text
Requirement
    |
    v
Requirement Analyzer
    |
    v
RequirementAnalysis
    |
    v
Test Case Generator
    |
    v
TestCaseResponse
    |
    v
Test Case Reviewer
    |
    v
TestCaseReview
    |
    v
QASuiteResult
```

Core MCP capabilities include:

``` text
health
test_llm
analyze_requirement
generate_test_cases
review_test_cases
generate_qa_suite
```

------------------------------------------------------------------------

# 7. Phase 2 --- QA Platform Foundation

## Completed milestones

  -----------------------------------------------------------------------
  Milestone               Capability              Status
  ----------------------- ----------------------- -----------------------
  P2-S1                   QA Project Context      COMPLETE

  P2-S2                   SQLite Persistence      COMPLETE

  P2-S3                   Requirement & Suite     COMPLETE
                          Versioning

  P2-S4                   Project Import / Export COMPLETE

  P2-S5                   Jira Connector          COMPLETE

  P2-S6                   GitHub Connector        COMPLETE

  P2-S8                   Automation Case /       COMPLETE through
                          Generation Pipeline     current committed
                                                  automation milestones

  P2-S8.10                Execution foundation    COMPLETE as committed
                                                  contract/boundary

  P2-S8.10.x              Controlled local        IN PROGRESS
                          execution pipeline
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 8. Project Context and Persistence

QA project context is represented by persistent project data.

Conceptually:

``` text
QAProject
    |
    +-- project_id
    +-- name
    +-- description
    +-- application
    +-- environment
    +-- metadata
    +-- requirements
    +-- test suites
```

Persistence architecture:

``` text
ProjectContext
      |
      v
ProjectRepository
      |
      v
SQLiteProjectRepository
      |
      v
SQLite
```

Database:

``` text
data/qa_mcp.db
```

Important rule:

> Never delete the persistent database merely to make tests pass.

Persistence-focused tests should use isolated database state.

------------------------------------------------------------------------

# 9. Requirement and Suite Versioning

Requirements are immutable versions:

``` text
Requirement V1
Requirement V2
Requirement V3
```

Suite versions retain their relationship to requirement versions:

``` text
Requirement Version
        |
        v
QA Suite Version
        |
        +-- Test Cases
        |
        +-- Review
```

Import/export validates structure and protects against duplicate project
IDs.

------------------------------------------------------------------------

# 10. Jira Connector

Jira is implemented behind an abstraction:

``` text
MCP
 |
 v
JiraService
 |
 v
JiraClient
 +-- MockJiraClient
 +-- JiraCloudClient
```

Current real Jira operations are read-only:

``` text
get_jira_issue(issue_key)
search_jira_issues(jql, max_results=50)
```

No Jira write operations are currently part of the completed connector
milestone.

The connector remains disabled by default unless configured.

------------------------------------------------------------------------

# 11. GitHub Connector

GitHub follows the same isolation pattern:

``` text
MCP
 |
 v
GitHubService
 |
 v
GitHubClient
 +-- MockGitHubClient
 +-- GitHubCloudClient
          |
          v
      GitHub REST API
```

Current read-only MCP tools:

``` text
get_github_repository(owner, repository)
get_github_issue(owner, repository, issue_number)
get_github_pull_request(owner, repository, pull_number)
search_github_issues(query, max_results=50)
```

Current cloud operations:

``` text
GET repository
GET issue
GET pull request
GET /search/issues
```

GitHub remains disabled without valid configuration.

No GitHub write operations are currently part of the completed connector
milestone.

------------------------------------------------------------------------

# 12. Automation Pipeline

The automation work has progressed beyond the original
automation-case-generator milestone.

Current conceptual pipeline:

``` text
Test Cases
    |
    v
Automation Candidate Selection
    |
    v
Automation Case
    |
    v
Automation Validation
    |
    v
Framework-specific Code Generation
    |
    v
GeneratedAutomationArtifact
    |
    v
Controlled Execution
    |
    v
AutomationExecutionResult
```

The project deliberately does not blindly automate every generated test
case.

Candidate selection exists to distinguish:

``` text
Recommended for automation
            |
            +---- Automated
            |
            +---- Manual-only
```

------------------------------------------------------------------------

# 13. Automation Code Generation

The current generated automation artifact contains:

``` text
GeneratedAutomationArtifact
    |
    +-- id
    +-- automation_case_id
    +-- framework
    +-- language
    +-- file_name
    +-- code
```

The current execution target is:

``` text
Framework: Playwright
Language: Python
```

Generated automation must be validated before downstream execution.

------------------------------------------------------------------------

# 14. Automation Execution Contract

The execution result is represented by:

``` text
AutomationExecutionResult
    |
    +-- execution_id
    +-- automation_artifact_id
    +-- automation_case_id
    +-- status
    +-- exit_code
    +-- stdout
    +-- stderr
    +-- duration_seconds
    +-- error
```

The `automation_case_id` traceability is intentional and must be
preserved.

Execution statuses currently include:

``` text
NOT_EXECUTED
PASSED
FAILED
TIMEOUT
ERROR
```

The status mapping should remain deterministic.

------------------------------------------------------------------------

# 15. Controlled Automation Execution Pipeline

The current local execution increment introduces three supporting
components.

## Execution configuration

``` text
AutomationExecutionConfig
    |
    +-- timeout_seconds = 60
    +-- workspace_root = optional
```

The configuration is immutable.

## Automation workspace

`AutomationWorkspace` creates an isolated temporary directory for an
automation artifact.

Conceptually:

``` text
GeneratedAutomationArtifact
        |
        v
AutomationWorkspace.create()
        |
        v
temporary execution directory
        |
        +-- generated test file
```

The workspace is cleaned up after execution unless explicit retention is
requested.

This prevents generated artifacts from being written directly into the
project working tree during normal execution.

## Controlled subprocess runner

`AutomationExecutionRunner` provides the subprocess boundary.

It:

-   accepts an explicit command list
-   runs from a supplied working directory
-   captures stdout
-   captures stderr
-   captures exit code
-   measures execution duration
-   enforces a timeout
-   reports timeout separately
-   reports operating-system execution errors separately

The runner is intentionally injectable so that tests do not need to
execute real automation processes.

------------------------------------------------------------------------

# 16. Current Execution Service Design

The execution service validates the generated artifact before execution.

Current validation rules:

``` text
Empty code
    -> ValueError

Missing framework
    -> ValueError

Unsupported framework
    -> ValueError
```

Current supported framework:

``` text
Playwright
```

For the current Python/Playwright execution path, the service constructs
a command equivalent to:

``` text
python -m pytest <generated_file_name>
```

The command is executed inside the temporary automation workspace.

The service maps raw runner results to the domain-level execution
result:

``` text
Runner exit_code == 0
    -> PASSED

Runner exit_code != 0
    -> FAILED

Runner timed_out
    -> TIMEOUT

Runner execution error
    -> ERROR
```

This separation is important:

``` text
Runner
    = process mechanics

ExecutionService
    = QA execution semantics

AutomationExecutionResult
    = stable domain contract
```

------------------------------------------------------------------------

# 17. Execution Safety Direction

The current subprocess runner is a **controlled local execution
boundary**, not yet the final production-grade sandbox.

The intended progression is:

``` text
Current
Local controlled subprocess
        |
        v
Hardened execution boundary
        |
        v
Container / isolated execution
        |
        v
Cloud or CI execution
```

Do not introduce arbitrary shell execution or unbounded command
construction.

Generated automation should remain restricted to supported frameworks
and controlled command construction.

Containerization should be added after the local execution contract and
orchestration behavior are stable.

------------------------------------------------------------------------

# 18. MCP Automation Execution Tool

The MCP boundary currently exposes:

``` text
execute_automation_code(artifact)
```

The MCP tool:

1.  validates the incoming artifact through
    `GeneratedAutomationArtifact`
2.  delegates to `AutomationExecutionService`
3.  returns `AutomationExecutionResult.model_dump()`
4.  converts invalid execution-artifact input into a controlled
    MCP-facing error

The intended architecture remains:

``` text
MCP Tool
   |
   v
Execution Service
   |
   +--> Workspace
   |
   +--> Runner
   |
   v
Execution Result
```

The MCP layer must not contain subprocess implementation details.

------------------------------------------------------------------------

# 19. Execution Tests

Current execution-focused tests cover:

``` text
AutomationExecutionResult
AutomationExecutionService
AutomationExecutionRunner
AutomationWorkspace
MCP execution tool
```

Current focused result:

``` text
16 passed, 1 warning
```

Current service result:

``` text
7 passed
```

The full project regression remains:

``` text
190 passed, 7 warnings
```

------------------------------------------------------------------------

# 20. Current MCP Capabilities

The repository currently exposes capabilities covering:

``` text
health
test_llm

analyze_requirement
generate_test_cases
review_test_cases
generate_qa_suite

create_qa_project
get_qa_project

create_requirement_version
get_requirement_version
list_requirement_versions

create_suite_version
get_suite_version
list_suite_versions

export_qa_project
import_qa_project

get_jira_issue
search_jira_issues

get_github_repository
get_github_issue
get_github_pull_request
search_github_issues

automation candidate / generation capabilities
execute_automation_code
```

The exact registered tool list should always be verified from the
running repository rather than assumed from this document.

------------------------------------------------------------------------

# 21. Testing Strategy

Every meaningful feature should follow the layered testing model.

For integrations:

``` text
Configuration
      |
      v
Interface / Client Abstraction
      |
      v
Mock Client
      |
      v
Core Service
      |
      v
Cloud Client
      |
      v
Factory
      |
      v
Runtime Wiring
      |
      v
MCP Tool
      |
      v
MCP Registration
      |
      v
Full Regression
```

For automation execution:

``` text
Result Contract
      |
      v
Workspace
      |
      v
Runner
      |
      v
Execution Service
      |
      v
MCP Tool
      |
      v
Full Regression
```

Tests must remain deterministic and repeatable.

------------------------------------------------------------------------

# 22. Current Regression Commands

Activate the environment:

``` bash
source .venv/bin/activate
```

Run all tests:

``` bash
pytest -q
```

Run execution tests:

``` bash
pytest -q \
tests/test_automation_execution_result.py \
tests/test_automation_execution_service.py \
tests/test_automation_execution_runner.py \
tests/test_automation_workspace.py \
tests/test_automation_execution_tool.py
```

Check formatting/whitespace problems:

``` bash
git diff --check
```

Check Git state:

``` bash
git status
```

Check recent history:

``` bash
git log -5 --oneline
```

Run the server:

``` bash
python -m qa_mcp.server
```

Verify server import:

``` bash
python -c "from qa_mcp.server import mcp; print('MCP Server import OK')"
```

Verify registered automation tools:

``` bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools() if 'automation' in t.name])"
```

------------------------------------------------------------------------

# 23. Known Warnings

There are currently 7 non-blocking pytest warnings.

Two categories are present.

## Pytest collection warnings

Pytest reports that Pydantic models such as:

``` text
TestCase
TestCaseReview
```

cannot be collected as pytest classes because they have constructors.

These are collection warnings caused by naming/domain-model interaction
and are not test failures.

## Pydantic settings warning

There is also:

``` text
IncompleteFieldDefinitionWarning
```

concerning:

``` text
Field 'lifespan'
```

from `pydantic_settings`.

Policy:

-   known
-   non-blocking
-   does not currently fail tests
-   should not be suppressed merely to make output clean
-   should be handled as separate technical debt unless it becomes
    relevant to the current feature

Do not mix warning cleanup into unrelated automation work.

------------------------------------------------------------------------

# 24. Security Rules

Never commit:

``` text
.env
real Jira tokens
real GitHub tokens
passwords
AWS credentials
private keys
organisation secrets
```

Before pushing:

``` bash
git status
git diff
git diff --cached
git check-ignore .env
```

Never put credentials into:

-   source code
-   README
-   test fixtures
-   Git remote URLs
-   committed configuration

The Git remote should remain credential-free.

------------------------------------------------------------------------

# 25. Configuration

The application uses configuration plus environment variables.

Typical connector values include:

``` text
JIRA_URL
JIRA_EMAIL
JIRA_API_TOKEN

GITHUB_URL
GITHUB_TOKEN
GITHUB_OWNER
```

External connectors are disabled by default where appropriate.

A local `.env` may be created:

``` bash
touch .env
```

The real file must remain ignored by Git.

------------------------------------------------------------------------

# 26. Git Checkpoint Procedure

Do not commit immediately after tests merely because the suite is green.

Before a milestone commit:

``` bash
pytest -q
git diff --check
git status
git diff
```

Review:

-   source changes
-   tests
-   README
-   secrets
-   unrelated modifications

Then stage the complete logical milestone:

``` bash
git add .
```

Review the staged change:

``` bash
git diff --cached --stat
git diff --cached
```

Then commit:

``` bash
git commit -m "Complete <checkpoint>"
```

Push:

``` bash
git push
```

Verify:

``` bash
git status
git branch -vv
git log --oneline --decorate -10
```

Desired result:

``` text
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

------------------------------------------------------------------------

# 27. Current Uncommitted Execution Checkpoint

The current development increment is:

``` text
P2-S8.10.x — Controlled Local Automation Execution
```

Current state:

``` text
Execution Result Contract             COMPLETE
Execution Service Boundary            COMPLETE
Execution Config                      COMPLETE
Execution Workspace                   COMPLETE
Controlled Subprocess Runner          COMPLETE
Service → Runner integration          COMPLETE
Status mapping                        COMPLETE
Timeout handling                      COMPLETE
Workspace cleanup                     COMPLETE
MCP execution boundary                COMPLETE
Focused tests                         GREEN
Full regression                       GREEN
README checkpoint                     THIS DOCUMENT
Git commit                            PENDING
Git push                              PENDING
```

Current verified regression:

``` text
190 passed, 7 warnings
```

Current committed baseline:

``` text
703cdb1 Complete automation execution foundation
```

The next commit should capture the controlled local execution pipeline
once the staged diff has been reviewed.

------------------------------------------------------------------------

# 28. Milestone History

Important recent milestones:

``` text
1d2360b  Add automation candidate pipeline
a226e9e  Add automation case validation
5ced4e3  Add automation code generation
715ad52  Complete P2-S8.8 automation code generation
703cdb1  Complete automation execution foundation
```

The automation development progression is:

``` text
Candidate Pipeline
       |
       v
Automation Case Validation
       |
       v
Automation Code Generation
       |
       v
Execution Result Contract
       |
       v
Execution Foundation
       |
       v
Controlled Local Execution
       |
       v
Hardened / Container Execution
       |
       v
Execution Reporting
```

------------------------------------------------------------------------

# 29. Remaining Major Development Work

The exact schedule should be driven by verified implementation rather
than arbitrary dates.

Major remaining product areas include:

## Automation execution

``` text
Controlled local execution          CURRENT
Execution hardening                 NEXT
Container isolation                 NEXT
Browser/runtime provisioning        NEXT
Execution artifact retention        NEXT
Result persistence                  NEXT
Screenshots / traces / videos       NEXT
Execution reporting                 NEXT
```

## QA intelligence

``` text
Agent / orchestrator
Cross-capability reasoning
Coverage analysis
Risk-based prioritization
Regression selection
Failure analysis
```

## Integrations

``` text
Jira write workflow
Jira → QA workflow
GitHub write workflow
PR-based automation workflow
CI/CD integration
Slack notifications
```

## Product layer

``` text
Web UI
Project dashboard
Requirement workspace
QA suite management
Automation workspace
Execution history
Reports
User/project configuration
Authentication
Hosted deployment
```

The order should remain deliberate. Do not start broad UI work by
bypassing unstable core services.

------------------------------------------------------------------------

# 30. Intended Full Product Architecture

The eventual product should look conceptually like:

``` text
                         USER
                          |
                          v
                    QA MCP UI / API
                          |
                          v
                    QA Agent Layer
                          |
          +---------------+----------------+
          |               |                |
          v               v                v
   QA Intelligence   Automation       Integrations
          |               |                |
          |               |          +-----+-----+
          |               |          |     |     |
          v               v          Jira GitHub Slack
    Requirement      Candidate
    Analysis         Selection
          |               |
          v               v
    Test Cases       Automation Cases
          |               |
          v               v
       Review         Validation
          |               |
          +-------+-------+
                  |
                  v
          Generated Automation
                  |
                  v
          Execution Orchestrator
                  |
          +-------+--------+
          |                |
          v                v
       Local            Container
       Runner            Runner
          |                |
          +-------+--------+
                  |
                  v
          Execution Results
                  |
                  v
           QA Reporting
                  |
                  v
           Persistent Context
```

This is the target direction, not a claim that all components are
already implemented.

------------------------------------------------------------------------

# 31. Fresh-Chat Continuity Instructions

When continuing QA MCP in a new chat:

``` bash
cd qa-mcp
source .venv/bin/activate
git pull
git status
git log -5 --oneline
pytest -q
```

At the current checkpoint, expect the committed repository to be at or
beyond:

``` text
703cdb1 Complete automation execution foundation
```

If the controlled execution commit has already been made, use the latest
Git checkpoint instead.

Then:

1.  Read this README.
2.  Inspect the current repository.
3.  Confirm Git status.
4.  Run `pytest -q`.
5.  Confirm the current regression baseline.
6.  Inspect the latest execution implementation.
7.  Do not recreate completed work.
8.  Continue from the next documented development increment.
9.  Follow the test-first and layered-architecture rules.
10. Update this README again before the next milestone commit.

------------------------------------------------------------------------

# 32. Fresh-Chat Handover Statement

Use the following as the continuity statement when starting a new
development session:

``` text
Resume QA MCP development from the latest GitHub/README checkpoint.

The project is a layered AI-powered QA MCP platform being developed
incrementally and test-first.

Phase 1 is complete.

Phase 2 completed foundations:
- QA Project Context
- SQLite Persistence
- Requirement and Suite Versioning
- Project Import / Export
- Jira read-only connector
- GitHub read-only connector

Automation pipeline completed through:
- candidate selection
- automation case validation
- automation code generation
- execution result contract
- execution foundation

The current automation execution increment establishes:
- AutomationExecutionConfig
- AutomationWorkspace
- AutomationExecutionRunner
- ExecutionService integration
- deterministic execution status mapping
- timeout handling
- workspace cleanup
- MCP execution boundary

Current verified local regression:
190 passed, 7 warnings.

The known warnings are non-blocking pytest/Pydantic warnings and should
remain separate technical debt unless they become relevant.

Development rules:
- work one increment at a time
- test first
- never weaken tests
- preserve layered architecture
- keep external dependencies mockable
- keep core logic independent of MCP transport
- validate AI output
- never commit secrets
- run focused tests
- run full regression
- verify runtime/MCP path
- update README
- review staged diff
- commit and push
- never recreate completed work

Latest committed checkpoint:
703cdb1 Complete automation execution foundation

Next technical direction:
finish and harden the controlled local Playwright execution path,
then introduce stronger isolation/container execution, execution
artifacts/results, reporting, and eventually QA-agent orchestration.

Do not jump directly to the UI or production deployment layer while
the core execution/orchestration contracts are still being stabilized.
```

------------------------------------------------------------------------

# 33. Final Continuity Rule

This README is the **development checkpoint**, not a substitute for the
repository.

The authoritative implementation sources are:

``` text
Source code
Tests
Configuration
Git history
```

The README records:

``` text
What is complete
What is in progress
What has been verified
What must not be recreated
What should happen next
How development must be performed
```

Every verified milestone must leave the repository in a reproducible
state:

``` text
Focused tests GREEN
        +
Full regression GREEN
        +
Runtime/MCP verification
        +
README updated
        +
Git checkpoint
        +
Remote synchronized
```

**Current verified baseline: 190 passed, 7 warnings.**

**Current committed baseline: `703cdb1` --- Complete automation
execution foundation.**

**Current development focus: controlled local automation execution.**
