# QA MCP

QA MCP is a Model Context Protocol (MCP) server for structured software-quality workflows.

The project is being developed incrementally toward a full-fledged AI-powered QA platform using:

- Layered architecture
- Test-first development
- Pydantic-based contracts
- Persistent SQLite storage
- Immutable QA versioning
- Project import/export
- Safe external connectors
- MCP tool boundaries
- LLM-assisted QA analysis and automation generation
- Automation candidate selection
- Playwright automation generation
- Controlled automation execution
- Eventual QA-agent orchestration
- Eventual CI/CD and hosted product capabilities

> **Continuity Rule:** This README is the authoritative development checkpoint for future QA MCP development sessions. Read it before starting new development. Do not recreate completed work.

---

# 1. Current Development Checkpoint

## Repository checkpoint

```text
Branch:             main
Latest commit:      3bdf761 Implement controlled automation execution
Previous commit:    703cdb1 Complete automation execution foundation
Remote:             origin/main
Working tree:       clean
Current milestone:  Controlled Automation Execution
Current checkpoint: P2-S8.9 — Controlled Automation Execution COMPLETE
```

The repository has now progressed beyond the original execution-foundation contract.

## Latest verified regression

```text
190 passed
7 warnings
0 failures
```

Focused execution suite:

```text
16 passed
1 warning
```

Execution-service suite:

```text
7 passed
```

Latest verification performed before the checkpoint:

```bash
pytest -q
git diff --check
git status
```

Result:

```text
190 passed, 7 warnings
git diff --check -> clean
working tree -> clean
```

## Latest committed implementation

The current committed execution pipeline contains:

```text
GeneratedAutomationArtifact
        |
        v
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
MCP execute_automation_code
```

The implementation is deliberately limited to a controlled local execution boundary. It is **not yet the final production-grade sandbox/container/cloud execution architecture**.

---

# 2. Product Vision

The long-term goal is to evolve QA MCP from a collection of QA utilities into an intelligent QA agent/platform.

The intended end-to-end flow is:

```text
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

Eventually the platform should support integrations such as:

```text
Jira
GitHub
Slack
CI/CD
Test repositories
Automation environments
Cloud execution
```

The UI/hosted product layer should be introduced after the core QA capabilities and agent workflow are sufficiently stable.

---

# 3. Development Rules — MUST FOLLOW

These rules apply to every future change.

1. Implement one phase/sub-step at a time.
2. Test first wherever practical.
3. Focused tests must pass before moving to the next implementation increment.
4. The relevant feature test group must pass.
5. The full regression suite must pass before closing a milestone.
6. Never weaken or delete tests merely to obtain green output.
7. Inspect existing code before modifying it.
8. Preserve the layered architecture.
9. Core business logic must remain independent of MCP transport.
10. Persistence must remain behind repository interfaces.
11. External integrations must remain mockable.
12. LLM providers must remain replaceable.
13. AI output must be validated before downstream use.
14. Do not commit secrets or real `.env` files.
15. Do not delete persistent databases merely to make tests pass.
16. Keep unrelated refactoring separate from feature work.
17. A major capability is not complete until its MCP/runtime path is verified.
18. Update this README at every verified milestone.
19. Commit only after the feature, tests, README, and checkpoint have been reviewed.
20. Do not recreate completed work from earlier milestones.
21. Do not introduce production-grade container/cloud complexity before the local execution contract is stable.
22. Keep generated automation execution behind explicit framework validation and controlled command construction.

The recurring development sequence is:

```text
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

---

# 4. Architecture

The fundamental architecture is:

```text
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
              |                       |               +--------+--------+
              |                       |               |        |        |
              v                       v               Jira    GitHub   Slack
     Requirement Analyzer       Automation             |        |        |
     Test Case Generator        Execution              v        v        v
     Test Case Reviewer         Versioning           Service  Service  Service
     QA Suite Workflow          Project Context        |        |        |
     Candidate Selection                             v        v        v
     Automation Generation                         Client   Client   Client
     Automation Execution                            / \      / \      / \
                                                     Mock     Mock    Mock
                                                     Cloud    Cloud   Cloud
```

Layer responsibilities:

```text
models/
    Domain and data contracts

core/
    Business/application services
    Factories
    Orchestration boundaries
    Automation execution mechanics

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

---

# 5. Repository Structure

Current important structure:

```text
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

---

# 6. Completed Product Capabilities

## Phase 1 — Foundation & QA Intelligence

**Status: COMPLETE**

Completed capabilities include:

- MCP server foundation
- Configuration loading
- LLM abstraction
- Mock LLM support
- Requirement analysis
- Test-case generation
- Test-case review
- End-to-end QA suite workflow

Core flow:

```text
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

```text
health
test_llm
analyze_requirement
generate_test_cases
review_test_cases
generate_qa_suite
```

---

# 7. Phase 2 — QA Platform Foundation

Completed milestones:

| Milestone | Capability | Status |
|---|---|---|
| P2-S1 | QA Project Context | COMPLETE |
| P2-S2 | SQLite Persistence | COMPLETE |
| P2-S3 | Requirement & Suite Versioning | COMPLETE |
| P2-S4 | Project Import / Export | COMPLETE |
| P2-S5 | Jira Connector | COMPLETE |
| P2-S6 | GitHub Connector | COMPLETE |
| P2-S8 | Automation Pipeline | COMPLETE through current automation checkpoints |
| P2-S8.6 | Automation Candidate Selection | COMPLETE |
| P2-S8.7 | Candidate → Automation Generation | COMPLETE |
| P2-S8.8 | Automation Case Validation | COMPLETE |
| P2-S8.8+ | Automation Code Generation | COMPLETE |
| P2-S8.9 | Controlled Automation Execution | COMPLETE |

Slack integration also exists behind service/client abstractions.

---

# 8. Project Context and Persistence

QA project context is represented by persistent project data.

Conceptually:

```text
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

```text
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

```text
data/qa_mcp.db
```

Important rule:

> Never delete the persistent database merely to make tests pass.

Persistence-focused tests should use isolated database state.

---

# 9. Requirement and Suite Versioning

Requirements are immutable versions:

```text
Requirement V1
Requirement V2
Requirement V3
```

Suite versions retain their relationship to requirement versions:

```text
Requirement Version
        |
        v
QA Suite Version
        |
        +-- Test Cases
        |
        +-- Review
```

Import/export validates structure and protects against duplicate project IDs.

---

# 10. External Connectors

## Jira

Jira is implemented behind an abstraction:

```text
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

```text
get_jira_issue(issue_key)
search_jira_issues(jql, max_results=50)
```

No Jira write operations are part of the completed connector milestone.

The connector remains disabled by default unless configured.

## GitHub

GitHub follows the same isolation pattern:

```text
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

```text
get_github_repository(owner, repository)
get_github_issue(owner, repository, issue_number)
get_github_pull_request(owner, repository, pull_number)
search_github_issues(query, max_results=50)
```

No GitHub write operations are part of the completed connector milestone.

## Slack

Slack is implemented behind:

```text
SlackService
    |
    v
SlackClient
    +-- MockSlackClient
    +-- SlackCloudClient
```

Current Slack MCP tools include:

```text
get_slack_channel
get_slack_messages
search_slack_messages
get_slack_thread
```

---

# 11. Automation Pipeline

The automation work has progressed well beyond the original automation-case-generator milestone.

Current pipeline:

```text
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

The project deliberately does not blindly automate every generated test case.

Candidate selection distinguishes:

```text
Recommended for automation
        |
        +---- Automated
        |
        +---- Manual-only
```

---

# 12. Automation Candidate Selection — P2-S8.6 COMPLETE

The candidate selector determines which test cases are suitable for automation.

The result is:

```text
AutomationCandidateResult
```

with:

```text
candidate_ids
manual_ids
total
```

MCP tool:

```text
select_automation_candidates
```

Candidate selection remains independent of the existing QA suite workflow so that it can be reused by future agent workflows.

---

# 13. Candidate → Automation Generation — P2-S8.7 COMPLETE

The orchestration service is:

```text
AutomationCandidateGenerationService
```

Its responsibility is deliberately narrow:

```text
TestCase[]
    |
    v
Candidate Selection
    |
    v
candidate_ids
    |
    v
Generate automation ONLY for candidates
    |
    v
AutomationCase[]
```

Manual-only test cases are not sent to the automation generator.

The zero-candidate case is explicitly handled:

```text
No automation candidates
        |
        v
[]
        |
        v
Automation generator is NOT called
```

MCP tool:

```text
generate_automation_for_candidates
```

Automation capabilities now include:

```text
generate_automation
    -> Generate automation for a known test case

select_automation_candidates
    -> Identify which test cases should be automated

generate_automation_for_candidates
    -> Select candidates and generate automation for them
```

---

# 14. Automation Case Validation — P2-S8.8 COMPLETE

The automation pipeline includes a dedicated validation layer.

Validator:

```text
AutomationValidator
```

Structured result:

```text
AutomationValidationResult
```

with:

```text
automation_case_id
test_case_id
valid
errors
warnings
```

Fundamental integrity includes:

- An automation case must contain at least one step.
- Validation failures are returned as structured errors.
- Non-blocking concerns can be returned as warnings.
- Validation is separated from automation generation.

Pipeline:

```text
Test Case
    |
    v
Candidate Selection
    |
    v
Automation Generation
    |
    v
Automation Case
    |
    v
Automation Validation
    |
    v
Validated Automation Case
```

---

# 15. Automation Code Generation

Generated automation artifacts are represented by:

```text
GeneratedAutomationArtifact
    |
    +-- id
    +-- automation_case_id
    +-- framework
    +-- language
    +-- file_name
    +-- code
```

Current execution target:

```text
Framework: Playwright
Language: Python
```

Generated automation must be validated before downstream execution.

The framework boundary is deliberately explicit. Unsupported frameworks must not silently fall through to arbitrary execution.

---

# 16. Automation Execution Contract

Execution results are represented by:

```text
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

The `automation_case_id` traceability is intentional and must be preserved.

Current statuses:

```text
NOT_EXECUTED
PASSED
FAILED
TIMEOUT
ERROR
```

Status mapping is deterministic.

---

# 17. Controlled Automation Execution — P2-S8.9 COMPLETE

The current committed execution increment introduces three supporting components.

## 17.1 Execution configuration

```text
AutomationExecutionConfig
    |
    +-- timeout_seconds = 60
    +-- workspace_root = optional
```

The configuration is immutable.

## 17.2 Automation workspace

`AutomationWorkspace` creates an isolated temporary directory for an automation artifact.

Conceptually:

```text
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

The workspace is cleaned up after execution unless explicit retention is requested.

This prevents generated artifacts from being written directly into the project working tree during normal execution.

## 17.3 Controlled subprocess runner

`AutomationExecutionRunner` provides the subprocess boundary.

It:

- accepts an explicit command list
- runs from a supplied working directory
- captures stdout
- captures stderr
- captures exit code
- measures execution duration
- enforces a timeout
- reports timeout separately
- reports operating-system execution errors separately

The runner is injectable so tests do not need to execute real automation processes.

---

# 18. Current Execution Service Design

The execution service validates the generated artifact before execution.

Current validation rules:

```text
Empty code
    -> ValueError

Missing framework
    -> ValueError

Unsupported framework
    -> ValueError
```

Current supported framework:

```text
Playwright
```

For the current Python/Playwright execution path, the service constructs:

```text
python -m pytest <generated_file_name>
```

The command is executed inside the temporary automation workspace.

Raw runner results are mapped to domain-level results:

```text
Runner exit_code == 0
    -> PASSED

Runner exit_code != 0
    -> FAILED

Runner timed_out
    -> TIMEOUT

Runner execution error
    -> ERROR
```

The separation is intentional:

```text
Runner
    = process mechanics

ExecutionService
    = QA execution semantics

AutomationExecutionResult
    = stable domain contract
```

Execution IDs are currently deterministic in the service foundation (`EX001`). A future persistence/execution-history layer should introduce durable unique execution IDs when execution history becomes a first-class capability.

---

# 19. Execution Safety Direction

The current subprocess runner is a controlled local execution boundary, not yet the final production-grade sandbox.

Intended progression:

```text
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

Security requirements:

- Do not introduce arbitrary shell execution.
- Do not construct unrestricted commands from user input.
- Keep framework support explicit.
- Keep generated filenames and execution paths controlled.
- Keep execution bounded by timeouts.
- Preserve workspace isolation.
- Keep the runner injectable and testable.
- Introduce containerization before exposing execution to untrusted production workloads.

Containerization should be added after the local execution contract and orchestration behavior are stable.

---

# 20. MCP Automation Execution Tool

The MCP boundary exposes:

```text
execute_automation_code(artifact)
```

The tool:

1. Validates the incoming artifact through `GeneratedAutomationArtifact`.
2. Delegates to `AutomationExecutionService`.
3. Returns `AutomationExecutionResult.model_dump()`.
4. Converts invalid execution-artifact input into a controlled MCP-facing error.

Architecture:

```text
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

---

# 21. Current MCP Automation Surface

Current automation-related MCP tools:

```text
generate_automation
select_automation_candidates
generate_automation_for_candidates
execute_automation_code
```

The first three represent candidate selection/generation.

`execute_automation_code` represents the controlled execution boundary.

Runtime verification remains a mandatory requirement whenever a major capability is closed.

---

# 22. Execution Tests

Execution-focused tests cover:

```text
AutomationExecutionResult
AutomationExecutionService
AutomationExecutionRunner
AutomationWorkspace
MCP execution tool
```

Current focused result:

```text
16 passed, 1 warning
```

Current execution-service result:

```text
7 passed
```

Full regression:

```text
190 passed, 7 warnings
```

No test was removed or weakened to achieve the current green baseline.

---

# 23. Current Automation Architecture

```text
                         TestCase[]
                             |
                             v
              +-----------------------------+
              | AutomationCandidateSelector |
              +-------------+---------------+
                            |
                            v
                AutomationCandidateService
                            |
                            v
                  AutomationCandidateResult
                     /                 \
            candidate_ids            manual_ids
                  |
                  v
       AutomationCandidateGenerationService
                  |
                  v
            AutomationService
                  |
                  v
         AutomationCaseGenerator
                  |
                  v
             AutomationCase[]
                  |
                  v
          AutomationValidator
                  |
                  v
       AutomationValidationResult
                  |
                  v
       CodeGenerationService
                  |
                  v
     GeneratedAutomationArtifact
                  |
                  v
       AutomationExecutionService
             /             \
            v               v
     AutomationWorkspace   Runner
             \             /
              \           /
               v         v
          AutomationExecutionResult
```

This separation is intentional.

The candidate selector decides **what should be automated**.

The automation generator decides **how it should be automated**.

The validator decides whether the generated automation case satisfies the minimum structural quality required for downstream processing.

The code-generation layer converts validated automation cases into executable framework-specific artifacts.

The execution service provides QA execution semantics.

---

# 24. Test Strategy

The project uses test-first development.

New capabilities are introduced by:

```text
Write failing test
        |
        v
Implement smallest production change
        |
        v
Run focused test
        |
        v
Run related tests
        |
        v
Run full regression
        |
        v
Verify runtime/MCP path
        |
        v
Update README
        |
        v
Review git diff
        |
        v
Commit code + tests + README
```

This discipline must continue throughout the remaining development.

---

# 25. Current Test Baseline

Latest committed checkpoint:

```text
190 passed
7 warnings
0 failures
```

Focused execution tests:

```text
16 passed
1 warning
```

Execution service tests:

```text
7 passed
```

The full regression suite must remain green before a feature checkpoint is committed.

---

# 26. Known Warnings / Technical Debt

There are currently two categories of non-blocking warnings.

## Pytest collection warnings

Some tests import Pydantic models named:

```text
TestCase
TestCaseReview
```

Pytest interprets these names as possible test classes and reports:

```text
PytestCollectionWarning
```

These do not represent functional failures.

They can be cleaned up later through test-only import aliases. This technical-debt cleanup should remain separate from feature implementation.

## Pydantic settings warning

There is also an existing warning related to the `lifespan` forward reference:

```text
IncompleteFieldDefinitionWarning
```

It originates from:

```text
pydantic_settings
```

and does not currently cause test failures.

Treat this as separate technical debt rather than mixing it into the automation execution feature work.

---

# 27. Configuration

Configuration is maintained under:

```text
config/settings.yaml
```

Environment-specific secrets should be supplied through environment variables.

Examples include:

```text
JIRA_API_TOKEN
GITHUB_TOKEN
SLACK_TOKEN
SLACK_DEFAULT_CHANNEL
```

Secrets must not be committed to Git.

---

# 28. Development Commands

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run all tests:

```bash
pytest -q
```

Run a specific test:

```bash
pytest -q tests/<test_file>.py
```

Check MCP tools:

```bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools()])"
```

Check automation tools:

```bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools() if 'automation' in t.name])"
```

Check formatting issues:

```bash
git diff --check
```

Check repository state:

```bash
git status
```

Review recent commits:

```bash
git log -5 --oneline
```

---

# 29. Git Checkpoint History

Important development checkpoints include:

```text
a288569 Initial commit with configured gitignore
1144ddd Resolve README.md merge conflict
882e149 Jira Connector Added
06dbe61 Complete GitHub connector
71c893e Initial commit with Slack Configured
169c1a1 Complete automation case generator
1d2360b Add automation candidate pipeline
a226e9e Add automation case validation
5ced4e3 Add automation code generation
715ad52 Complete P2-S8.8 automation code generation
703cdb1 Complete automation execution foundation
3bdf761 Implement controlled automation execution
```

Completed automation checkpoints:

```text
P2-S8.6  Automation Candidate Selection          COMPLETE
P2-S8.7  Candidate → Automation Generation       COMPLETE
P2-S8.8  Automation Case Validation              COMPLETE
P2-S8.8+ Automation Code Generation              COMPLETE
P2-S8.9  Controlled Automation Execution         COMPLETE
```

Each completed checkpoint must be committed together with:

```text
Implementation
Tests
README
Verification evidence
```

---

# 30. What Has Already Been Completed — DO NOT REBUILD

The following capabilities are already implemented and tested and must not be redesigned or recreated as if they were new work:

```text
MCP server foundation
Configuration
LLM abstraction
Mock LLM
Requirement analysis
Test case generation
Test case review
QA suite workflow
Project context
SQLite persistence
Requirement/suite versioning
Import/export
Jira connector
GitHub connector
Slack connector
Automation case generation
Automation candidate selection
Candidate → automation orchestration
Automation case validation
Playwright/Python automation code generation
GeneratedAutomationArtifact contract
AutomationExecutionResult contract
AutomationWorkspace
AutomationExecutionRunner
AutomationExecutionService
execute_automation_code MCP boundary
```

Future work must build on these components.

---

# 31. Next Development Checkpoint

## P2-S9 — Hardened Execution / Execution Evidence

**Status: NEXT**

The next work should not return to candidate selection, automation generation, validation, or the already-completed local execution boundary.

The immediate direction is to make the current execution capability more production-ready and useful.

Priority progression:

```text
P2-S8.9 Controlled local execution
        |
        v
P2-S9.1 Execution hardening
        |
        +-- safe workspace/file handling
        +-- stronger command validation
        +-- execution identity
        +-- configurable limits
        +-- better failure classification
        +-- artifact/result retention policy
        |
        v
P2-S9.2 Execution evidence
        |
        +-- generated artifact metadata
        +-- stdout/stderr evidence
        +-- execution metadata
        +-- result persistence
        +-- traceability
        |
        v
P2-S9.3 Execution history
        |
        v
P2-S9.4 Reporting / analysis
        |
        v
P2-S10 Agent orchestration
```

The exact sub-step should be defined and tested before implementation begins.

---

# 32. Future Execution Architecture

The target architecture should eventually become:

```text
GeneratedAutomationArtifact
        |
        v
Execution Policy / Safety Validation
        |
        v
Isolated Execution Environment
        |
        v
Framework Runner
        |
        v
Execution Evidence
        |
        v
Execution Result
        |
        v
Persistent Execution History
        |
        v
Reporting / AI Analysis
```

Potential future isolation options:

```text
Local hardened process
        |
        v
Docker/container
        |
        v
CI worker
        |
        v
Cloud execution
```

Do not implement all layers at once.

---

# 33. Eventual Agent-Driven QA Workflow

The eventual product experience should allow a user to provide a requirement and have the QA agent progressively execute the workflow:

```text
Understanding requirement...
        |
        v
Analyzing scenarios...
        |
        v
Generating test cases...
        |
        v
Reviewing coverage...
        |
        v
Identifying automation candidates...
        |
        v
Generating automation...
        |
        v
Validating automation...
        |
        v
Executing automation...
        |
        v
Analyzing results...
        |
        v
Preparing QA report...
```

The intention is not merely to expose MCP tools.

MCP should become the capability layer underneath an agent-driven QA product.

---

# 34. Eventual Product / UI Direction

The eventual UI should make the agent's progress, generated artifacts, execution state, and results visible and understandable.

Conceptually:

```text
User
  |
  v
QA MCP UI
  |
  v
Agent / MCP Orchestration
  |
  +-- Requirement analysis
  +-- Test generation
  +-- Test review
  +-- Candidate selection
  +-- Automation generation
  +-- Automation validation
  +-- Automation execution
  +-- Results / reporting
  +-- Jira
  +-- GitHub
  +-- Slack
```

The UI and hosted product layer should be introduced only after the core QA-agent capabilities are sufficiently stable.

---

# 35. Long-Term Product Direction

The final product should evolve toward a full-fledged QA intelligence platform capable of:

```text
Understand
    |
    v
Plan
    |
    v
Generate
    |
    v
Validate
    |
    v
Execute
    |
    v
Observe
    |
    v
Analyze
    |
    v
Report
    |
    v
Learn / Improve
```

The platform should eventually support:

- Requirements intelligence
- Test design
- Test review
- Automation selection
- Automation generation
- Automation validation
- Safe execution
- Execution evidence
- Failure analysis
- Coverage analysis
- Regression intelligence
- External engineering-system context
- CI/CD integration
- Agent orchestration
- Interactive UI
- Hosted/cloud execution

These are future goals, not permission to prematurely implement everything.

---

# 36. Development Principles

The following principles must remain unchanged as the project grows:

1. Build incrementally.
2. Write tests before implementation where practical.
3. Keep services small and composable.
4. Keep MCP tools thin.
5. Keep external integrations behind infrastructure abstractions.
6. Avoid destabilizing existing workflows when adding new capabilities.
7. Preserve structured Pydantic contracts.
8. Keep secrets outside source control.
9. Run the full regression suite before every feature checkpoint.
10. Update this README whenever a meaningful feature checkpoint is committed.
11. Commit code, tests and README together for each completed checkpoint.
12. Prefer explicit contracts over implicit behavior.
13. Prefer deterministic behavior over clever behavior.
14. Keep execution safety ahead of execution convenience.
15. Keep production concerns separated from prototype convenience.
16. Do not duplicate completed capabilities.
17. Do not silently change previously established contracts.
18. Maintain traceability from requirement → test case → automation case → artifact → execution result.

---

# 37. Current Resume Point

## Resume from:

**P2-S9.1 — Execution Hardening**

Previous completed checkpoints:

```text
P2-S8.6  Automation Candidate Selection          COMPLETE
P2-S8.7  Candidate → Automation Generation       COMPLETE
P2-S8.8  Automation Case Validation              COMPLETE
P2-S8.8+ Automation Code Generation              COMPLETE
P2-S8.9  Controlled Automation Execution         COMPLETE
```

Verified baseline:

```text
190 passed
7 warnings
0 failures
```

Latest commit:

```text
3bdf761 Implement controlled automation execution
```

Current automation MCP surface:

```text
generate_automation
select_automation_candidates
generate_automation_for_candidates
execute_automation_code
```

## Critical continuity instruction

A future development session must:

1. Read this README first.
2. Inspect the current GitHub `main` branch.
3. Confirm the latest commit and test baseline.
4. Inspect the existing implementation before proposing changes.
5. Start from **P2-S9.1**, not from an earlier automation milestone.
6. Do not recreate candidate selection, automation generation, validation, or controlled execution.
7. Add tests first wherever practical.
8. Keep the architecture layered.
9. Verify focused tests.
10. Verify the full regression suite.
11. Update this README at the end of every verified checkpoint.
12. Commit and push code + tests + README together.

This README is the project's continuity record and must be treated as part of the implementation, not as optional documentation.
