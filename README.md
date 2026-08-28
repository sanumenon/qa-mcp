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

> **CONTINUITY RULE:** This README is the authoritative development, deployment, roadmap, and continuity checkpoint for future QA MCP development sessions. Read it before starting new development. Do not recreate completed work.

---

# 1. CURRENT DEVELOPMENT CHECKPOINT

## Repository checkpoint

```text
Repository:          https://github.com/sanumenon/qa-mcp/tree/main
Branch:              main
Latest commit:       b6190d9 Harden automation workspace file handling
Previous commit:     731d483 Update project continuity documentation
Previous commit:     add5ba2 Update project continuity roadmap
Previous implementation checkpoint: 3bdf761 Implement controlled automation execution
Remote:              origin/main
Working tree before checkpoint: clean
Current checkpoint:  P2-S9.1.b.1 — Controlled Automation Command Boundary
Next implementation: P2-S9.1.b.2 — Further command/execution policy hardening
Checkpoint commit:   Pending user commit
```

## Latest verified baseline

```text
pytest -q
204 passed
7 warnings
0 failures

P2-S9.1.a focused execution suite:
28 passed
0 failures

git diff --check
clean

git status
working tree clean
```

The warnings are known non-blocking technical debt and are documented below.

## Latest completed automation checkpoint

```text
P2-S8.6   Automation Candidate Selection          COMPLETE
P2-S8.7   Candidate → Automation Generation       COMPLETE
P2-S8.8   Automation Case Validation              COMPLETE
P2-S8.8+  Automation Code Generation              COMPLETE
P2-S8.9   Controlled Automation Execution         COMPLETE
```

**Do not rebuild or redesign these completed checkpoints.**

---

# 2. PRODUCT VISION

The long-term goal is to evolve QA MCP from a collection of QA utilities into an intelligent QA agent/platform.

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

Eventually the platform should support:

```text
Jira
GitHub
Slack
CI/CD
Test repositories
Automation environments
Cloud execution
Interactive UI
Hosted/cloud product
```

The UI/hosted product layer must be introduced only after the core QA-agent capabilities are sufficiently stable.

---

# 3. DEVELOPMENT RULES — MUST FOLLOW

These rules apply to every future change.

1. Implement one phase/sub-step at a time.
2. Test first wherever practical.
3. Focused tests must pass before moving to the next increment.
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
14. Never commit secrets or a real `.env` file.
15. Never delete persistent databases merely to make tests pass.
16. Keep unrelated refactoring separate from feature work.
17. A major capability is not complete until its MCP/runtime path is verified.
18. Update this README at every verified milestone.
19. Commit only after feature, tests, README, and checkpoint have been reviewed.
20. Do not recreate completed work from earlier milestones.
21. Do not introduce production-grade container/cloud complexity before the local execution contract is stable.
22. Keep generated automation execution behind explicit framework validation and controlled command construction.
23. Preserve traceability:
    `Requirement → Test Case → Automation Case → Artifact → Execution Result`.
24. Do not silently change established contracts.
25. Prefer deterministic behavior over clever behavior.
26. Keep execution safety ahead of execution convenience.
27. Deployment/configuration details must remain documented here.
28. A new chat/session must begin from this README and the current GitHub `main` branch.

## Mandatory development sequence

```text
Read README / current checkpoint
        |
        v
Inspect GitHub main + repository state
        |
        v
Inspect existing implementation
        |
        v
Define ONE next sub-step
        |
        v
Write/update focused tests
        |
        v
Implement smallest production change
        |
        v
Focused tests green
        |
        v
Feature tests green
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
git diff --check
        |
        v
Commit + push
        |
        v
Verify clean working tree
```

---

# 4. ARCHITECTURE

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

# 5. REPOSITORY STRUCTURE

Important current structure:

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

# 6. COMPLETED PRODUCT CAPABILITIES

## Phase 1 — Foundation & QA Intelligence

**STATUS: COMPLETE**

Completed:

- MCP server foundation
- Configuration loading
- LLM abstraction
- Mock LLM support
- Requirement analysis
- Test-case generation
- Test-case review
- End-to-end QA suite workflow

Core MCP capabilities:

```text
health
test_llm
analyze_requirement
generate_test_cases
review_test_cases
generate_qa_suite
```

## Phase 2 — QA Platform Foundation

| Milestone | Capability | Status |
|---|---|---|
| P2-S1 | QA Project Context | COMPLETE |
| P2-S2 | SQLite Persistence | COMPLETE |
| P2-S3 | Requirement & Suite Versioning | COMPLETE |
| P2-S4 | Project Import / Export | COMPLETE |
| P2-S5 | Jira Connector | COMPLETE |
| P2-S6 | GitHub Connector | COMPLETE |
| P2-S8 | Automation Pipeline | COMPLETE through current checkpoints |
| P2-S8.6 | Automation Candidate Selection | COMPLETE |
| P2-S8.7 | Candidate → Automation Generation | COMPLETE |
| P2-S8.8 | Automation Case Validation | COMPLETE |
| P2-S8.8+ | Automation Code Generation | COMPLETE |
| P2-S8.9 | Controlled Automation Execution | COMPLETE |

Slack integration exists behind service/client abstractions.

---

# 7. PROJECT CONTEXT AND PERSISTENCE

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

Persistence:

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

**Important:** Never delete the persistent database merely to make tests pass.

Persistence-focused tests should use isolated database state.

---

# 8. EXTERNAL CONNECTORS

## Jira

Abstraction:

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

Current real operations are read-only:

```text
get_jira_issue(issue_key)
search_jira_issues(jql, max_results=50)
```

No Jira write operations are part of the completed connector milestone.

## GitHub

Abstraction:

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
```

Current read-only tools:

```text
get_github_repository(owner, repository)
get_github_issue(owner, repository, issue_number)
get_github_pull_request(owner, repository, pull_number)
search_github_issues(query, max_results=50)
```

No GitHub write operations are part of the completed connector milestone.

## Slack

Abstraction:

```text
SlackService
    |
    v
SlackClient
    +-- MockSlackClient
    +-- SlackCloudClient
```

Current tools include:

```text
get_slack_channel
get_slack_messages
search_slack_messages
get_slack_thread
```

---

# 9. AUTOMATION PIPELINE

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

Candidate selection deliberately distinguishes:

```text
Recommended for automation
        |
        +---- Automated
        |
        +---- Manual-only
```

Manual-only test cases must not be sent to the automation generator.

---

# 10. AUTOMATION CHECKPOINTS ALREADY COMPLETE

## P2-S8.6 — Candidate Selection

`AutomationCandidateSelector` / `AutomationCandidateService`

Result:

```text
AutomationCandidateResult
    +-- candidate_ids
    +-- manual_ids
    +-- total
```

MCP tool:

```text
select_automation_candidates
```

## P2-S8.7 — Candidate → Automation Generation

Service:

```text
AutomationCandidateGenerationService
```

Flow:

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

Zero-candidate behavior:

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

## P2-S8.8 — Automation Case Validation

Validator:

```text
AutomationValidator
```

Result:

```text
AutomationValidationResult
    +-- automation_case_id
    +-- test_case_id
    +-- valid
    +-- errors
    +-- warnings
```

Minimum integrity:

- At least one automation step.
- Validation failures are structured errors.
- Non-blocking concerns can be warnings.
- Validation remains separate from generation.

## P2-S8.8+ — Automation Code Generation

Artifact:

```text
GeneratedAutomationArtifact
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

---

# 11. CONTROLLED AUTOMATION EXECUTION — P2-S8.9 COMPLETE

The committed local execution pipeline is:

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

## Execution configuration

```text
AutomationExecutionConfig
    +-- timeout_seconds = 60
    +-- workspace_root = optional
```

The configuration is immutable.

## Automation workspace

`AutomationWorkspace` creates an isolated temporary directory for the generated artifact.

The workspace is cleaned up after execution unless explicit retention is requested.

The project working tree must not be used as the normal generated-artifact execution directory.

## Controlled subprocess runner

`AutomationExecutionRunner`:

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

## Execution service

Current validation:

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

Current Python execution command:

```text
python -m pytest <generated_file_name>
```

Status mapping:

```text
exit_code == 0
    -> PASSED

exit_code != 0
    -> FAILED

timed_out
    -> TIMEOUT

runner error
    -> ERROR
```

Separation:

```text
Runner
    = process mechanics

ExecutionService
    = QA execution semantics

AutomationExecutionResult
    = stable domain contract
```

Execution IDs are currently deterministic in the service foundation (`EX001`). Durable unique execution IDs belong to the future execution-history/persistence layer.

---

# 12. EXECUTION SAFETY REQUIREMENTS

The current subprocess runner is a controlled local execution boundary, **not** the final production-grade sandbox.

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

Mandatory safety direction:

- Do not introduce arbitrary shell execution.
- Do not construct unrestricted commands from user input.
- Keep framework support explicit.
- Keep generated filenames and execution paths controlled.
- Keep execution bounded by timeouts.
- Preserve workspace isolation.
- Keep the runner injectable and testable.
- Introduce containerization before exposing execution to untrusted production workloads.

Do not add container/cloud complexity before the local execution contract and orchestration behavior are stable.

---

# 13. MCP AUTOMATION SURFACE

Current automation-related MCP tools:

```text
generate_automation
select_automation_candidates
generate_automation_for_candidates
execute_automation_code
```

`execute_automation_code(artifact)`:

1. Validates the incoming artifact through `GeneratedAutomationArtifact`.
2. Delegates to `AutomationExecutionService`.
3. Returns `AutomationExecutionResult.model_dump()`.
4. Converts invalid execution-artifact input into a controlled MCP-facing error.

The MCP layer must not contain subprocess implementation details.

---

# 14. TEST STRATEGY AND CURRENT BASELINE

Test-first development remains mandatory.

Expected sequence:

```text
Write failing test
        |
        v
Implement smallest production change
        |
        v
Focused test
        |
        v
Related tests
        |
        v
Full regression
        |
        v
Runtime/MCP verification
        |
        v
README update
        |
        v
git diff --check
        |
        v
Commit + push
```

Current verified baseline before P2-S9.1.a:

```text
pytest -q
190 passed
7 warnings
0 failures
```

P2-S9.1.a verified regression:

```text
pytest -q
204 passed
7 warnings
0 failures
```

P2-S9.1.a focused execution suite:

```text
16 passed
1 warning
```

Execution service suite:

```text
7 passed
```

No test was removed or weakened to obtain the current green baseline.

---

# 15. KNOWN WARNINGS / TECHNICAL DEBT

## Pytest collection warnings

Pydantic models named:

```text
TestCase
TestCaseReview
```

can be interpreted by pytest as possible test classes, producing `PytestCollectionWarning`.

These are non-functional warnings.

Future cleanup may use test-only import aliases. Keep this separate from feature work.

## Pydantic settings warning

Existing:

```text
IncompleteFieldDefinitionWarning
```

related to the `lifespan` forward reference in `pydantic_settings`.

It does not currently cause test failures.

Keep this as separate technical debt unless it blocks development.

---

# 16. ENVIRONMENT / .ENV DOCUMENTATION

## Critical rule

The following is the **documented `.env` template currently used by the development setup**.

**These are placeholders, not real credentials.**

Never commit a real `.env` file, API token, password, or secret to Git.

The actual local `.env` remains developer-machine configuration.

## Current `.env` template

```dotenv
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email
JIRA_API_TOKEN=your-token
GITHUB_URL=https://api.github.com
GITHUB_TOKEN=your-github-token
GITHUB_OWNER=your-github-username-or-org
# ---------------------------------------------------------
# Slack
# ---------------------------------------------------------
SLACK_URL=https://slack.com/api
SLACK_TOKEN=
SLACK_DEFAULT_CHANNEL=
```

## Variable purpose

| Variable | Purpose | Secret? |
|---|---|---|
| `JIRA_URL` | Jira Cloud base URL | No |
| `JIRA_EMAIL` | Jira API account email | No, but treat as configuration |
| `JIRA_API_TOKEN` | Jira API authentication | **YES** |
| `GITHUB_URL` | GitHub API base URL | No |
| `GITHUB_TOKEN` | GitHub API authentication | **YES** |
| `GITHUB_OWNER` | GitHub username/org used by configuration | No |
| `SLACK_URL` | Slack API base URL | No |
| `SLACK_TOKEN` | Slack API authentication | **YES** |
| `SLACK_DEFAULT_CHANNEL` | Default Slack channel configuration | No |

## Deployment/configuration rule

When configuring a new environment:

1. Copy the documented template into a local `.env`.
2. Replace only the placeholder values required for that environment.
3. Never paste real secrets into this README.
4. Never commit the populated `.env`.
5. Verify `.gitignore` protects `.env`.
6. Keep configuration changes documented here when they materially affect deployment.
7. If new environment variables are introduced, update this section in the same development checkpoint.

---

# 17. CONFIGURATION

Primary configuration:

```text
config/settings.yaml
```

Environment-specific secrets are supplied through environment variables.

Known integration variables:

```text
JIRA_URL
JIRA_EMAIL
JIRA_API_TOKEN

GITHUB_URL
GITHUB_TOKEN
GITHUB_OWNER

SLACK_URL
SLACK_TOKEN
SLACK_DEFAULT_CHANNEL
```

Secrets must remain outside source control.

---

# 18. DEVELOPMENT ENVIRONMENT

Python requirement:

```text
Python >= 3.11
```

Current development environment used during the latest verification:

```text
Python 3.12 virtual environment
.venv/
```

Activate:

```bash
source .venv/bin/activate
```

Install project dependencies according to the repository's `requirements.txt`.

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

# 19. GIT CHECKPOINT HISTORY

Important checkpoints:

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
add5ba2 Update project continuity roadmap
```

Every completed checkpoint must contain:

```text
Implementation
Tests
README
Verification evidence
Commit
Push
Clean working tree
```

---

# 20. WHAT HAS ALREADY BEEN COMPLETED — DO NOT REBUILD

These capabilities are already implemented/tested and must not be redesigned or recreated as if they were new:

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

# 21. NEXT DEVELOPMENT CHECKPOINT

## P2-S9.1 — Execution Hardening

**STATUS: IN PROGRESS — P2-S9.1.b.1 COMPLETE**

Completed sub-step:

```text
P2-S9.1.b.1 — Controlled Automation Command Boundary
```

Next sub-step:

```text
P2-S9.1.b.2 — Further Command/Execution Policy Hardening
```

Do not return to:

- candidate selection
- automation generation
- automation validation
- already-completed controlled local execution foundation

Immediate direction:

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

P2-S9.1.a and P2-S9.1.b.1 are implemented and verified. The next sub-step must be defined and tested before implementation.

---

# 21A. COMPLETED CHECKPOINT — P2-S9.1.a

## Execution Hardening — Safe Workspace/File Handling

**STATUS: COMPLETE**

P2-S9.1.a hardens the generated automation workspace boundary without changing the established execution contracts or MCP execution flow.

Implemented:

- Strict generated artifact filename validation.
- Rejection of empty and whitespace-only filenames.
- Rejection of `.` and `..`.
- Rejection of POSIX absolute paths and traversal paths.
- Rejection of Windows-style traversal and drive-style paths.
- Explicit resolved-path containment verification before writing.
- Filename validation before workspace creation.
- Generated artifacts remain constrained to the controlled workspace.

Tests:

```text
14 new workspace-hardening tests
Focused execution suite: 28 passed
Full regression: 204 passed, 0 failures, 7 warnings
git diff --check: clean
```

The 7 warnings remain the existing non-blocking pytest/Pydantic technical debt documented in Section 15 and are intentionally outside this checkpoint.

No existing Pydantic execution contracts were changed.

**Next implementation: P2-S9.1.b.2 — Further command/execution policy hardening**

---

# 21B. COMPLETED CHECKPOINT — P2-S9.1.b.1

## Execution Hardening — Controlled Automation Command Boundary

**STATUS: COMPLETE**

Implemented:

- Explicit controlled command construction in `AutomationExecutionService`.
- Playwright automation is restricted to `python -m pytest <artifact_file_name>`.
- Unsupported automation frameworks are rejected before command construction.
- Unsafe artifact filenames are rejected before command construction.
- `AutomationExecutionRunner` remains a generic subprocess execution wrapper.
- Existing Pydantic execution contracts and the MCP execution boundary remain unchanged.

Tests:

```text
Focused execution service suite: 10 passed
Full regression: 207 passed, 0 failures, 7 warnings
git diff --check: clean
```

The 7 warnings remain the existing non-blocking pytest/Pydantic technical debt documented in Section 15.

**Next implementation: P2-S9.1.b.2 — Further command/execution policy hardening**

---

# 22. FUTURE EXECUTION ARCHITECTURE

Target:

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

Potential isolation progression:

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

# 23. EVENTUAL AGENT-DRIVEN QA WORKFLOW

The eventual product experience:

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

MCP is intended to become the capability layer underneath an agent-driven QA product.

---

# 24. EVENTUAL PRODUCT / UI DIRECTION

The eventual UI should make the agent's progress, generated artifacts, execution state, and results visible and understandable.

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

# 25. LONG-TERM PRODUCT DIRECTION

The final product should evolve toward:

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

Long-term capabilities:

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

# 26. DEVELOPMENT PRINCIPLES

The following principles must remain unchanged:

1. Build incrementally.
2. Write tests before implementation where practical.
3. Keep services small and composable.
4. Keep MCP tools thin.
5. Keep external integrations behind infrastructure abstractions.
6. Avoid destabilizing existing workflows.
7. Preserve structured Pydantic contracts.
8. Keep secrets outside source control.
9. Run full regression before every feature checkpoint.
10. Update this README whenever a meaningful feature checkpoint is committed.
11. Commit code, tests and README together for each completed checkpoint.
12. Prefer explicit contracts over implicit behavior.
13. Prefer deterministic behavior over clever behavior.
14. Keep execution safety ahead of execution convenience.
15. Keep production concerns separated from prototype convenience.
16. Do not duplicate completed capabilities.
17. Do not silently change established contracts.
18. Maintain requirement → test case → automation case → artifact → execution result traceability.
19. Treat deployment/configuration documentation as part of the implementation.
20. Treat this README as the continuity record, not optional documentation.

---

# 27. CURRENT RESUME POINT

## Resume from

**P2-S9.1.b.2 — Further Command/Execution Policy Hardening**

P2-S9.1.a — Safe Workspace/File Handling and P2-S9.1.b.1 — Controlled Automation Command Boundary are complete and must not be recreated.

Previous completed checkpoints:

```text
P2-S8.6   Automation Candidate Selection          COMPLETE
P2-S8.7   Candidate → Automation Generation       COMPLETE
P2-S8.8   Automation Case Validation              COMPLETE
P2-S8.8+  Automation Code Generation              COMPLETE
P2-S8.9   Controlled Automation Execution         COMPLETE
```

Verified baseline after P2-S9.1.b.1:

```text
207 passed
7 warnings
0 failures
```

Latest repository implementation commit:

```text
b6190d9 Harden automation workspace file handling
```

Current checkpoint commit:

```text
Pending user commit
```

Previous implementation checkpoint:

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

---

# 28. CRITICAL CONTINUITY INSTRUCTION FOR A NEW CHAT

A future development session must:

1. Read this README first.
2. Inspect the current GitHub `main` branch:
   `https://github.com/sanumenon/qa-mcp/tree/main`
3. Confirm the latest commit and test baseline.
4. Inspect the existing implementation before proposing changes.
5. Start from **P2-S9.1.b.2 — Further Command/Execution Policy Hardening**.
6. Treat **P2-S9.1.a — Safe Workspace/File Handling** as complete.
7. Treat **P2-S9.1.b.1 — Controlled Automation Command Boundary** as complete.
8. Do not recreate candidate selection.
9. Do not recreate automation generation.
10. Do not recreate automation validation.
11. Do not recreate controlled local execution.
12. Do not silently replace established architecture/contracts.
13. Add tests first wherever practical.
14. Keep the architecture layered.
15. Verify focused tests.
16. Verify the full regression suite.
17. Verify the MCP/runtime path for major capabilities.
18. Update this README at the end of every verified checkpoint.
19. Include deployment/configuration changes in this README.
20. Never commit real secrets or a populated `.env`.
21. Commit and push code + tests + README together.
22. Verify the working tree is clean after the checkpoint.
23. Never make the user repeat already-completed development work when the repository and README contain it.
24. Never use a new chat as a reason to restart the project from an earlier phase.

**This README is part of the implementation and must be treated as the project's authoritative continuity record.**
