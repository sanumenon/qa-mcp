# QA MCP

QA MCP is a Model Context Protocol (MCP) server for structured
software-quality workflows.

The project is developed incrementally using a layered architecture,
test-first implementation, persistent SQLite storage, immutable QA
versioning, project import/export, and safe external connectors.

> **Current checkpoint:** Phase 2 → GitHub Connector COMPLETE through
> S6.9\
> **Current regression:** **111 tests passing**\
> **Known warning:** one non-blocking third-party `pydantic_settings`
> warning related to `lifespan`.

------------------------------------------------------------------------

# 1. Current Development Status

## Phase 1 --- Foundation

**Status: COMPLETE**

-   MCP server foundation
-   Configuration loading
-   LLM abstraction
-   Requirement analysis
-   Test-case generation
-   Test-case review
-   Complete QA-suite workflow

## Phase 2 --- QA Platform Foundation

  Step    Capability                       Status
  ------- -------------------------------- -------------
  P2-S1   Project Context                  ✅ Complete
  P2-S2   SQLite Persistence               ✅ Complete
  P2-S3   Requirement & Suite Versioning   ✅ Complete
  P2-S4   Project Import / Export          ✅ Complete
  P2-S5   Jira Connector                   ✅ Complete
  P2-S6   GitHub Connector                 ✅ Complete

### Jira checkpoints

  Sub-step                                Status
  --------------------------------------- --------
  S5.1 Configuration                      ✅
  S5.2 Client Abstraction                 ✅
  S5.3 Service                            ✅
  S5.4 Cloud Client                       ✅
  S5.5 Read-only MCP Tools                ✅
  S5.6 Configuration Wiring               ✅
  S5.7 Controlled Integration Readiness   ✅

### GitHub checkpoints

  Sub-step                                     Status
  -------------------------------------------- --------
  S6.1 Configuration                           ✅
  S6.2 Client Abstraction + Models             ✅
  S6.3 Mock Client                             ✅
  S6.4 Service                                 ✅
  S6.5 Cloud/API Client                        ✅
  S6.6 Factory                                 ✅
  S6.7 Runtime Wiring                          ✅
  S6.8 Read-only MCP Tools + Disabled Safety   ✅
  S6.9 MCP Registration + Regression           ✅
  S6.10 README + Git Checkpoint                ⏳

Do not skip ahead without preserving this checkpoint.

------------------------------------------------------------------------

# 2. Development Guidelines

These rules are the baseline for all future development.

1.  **Incremental phases:** implement one phase/sub-step at a time.
2.  **Test first:** focused tests → fix → feature group → full
    regression.
3.  **Never weaken tests** just to obtain green output.
4.  **Preserve architecture:** MCP → Core Service → Infrastructure
    Interface → Concrete Implementation.
5.  **External integrations must be mockable.**
6.  **Never commit secrets** or real `.env` files.
7.  **README is part of every verified checkpoint.**
8.  **Inspect existing files before modifying them.**
9.  **Keep unrelated cleanup separate.**
10. **`pytest -q` is the authoritative regression baseline.**
11. Core business logic remains independent of MCP transport.
12. Persistence remains behind repository interfaces.
13. LLM providers remain replaceable.
14. AI output must be validated before downstream use.
15. Do not delete persistent databases merely to make tests pass.
16. A major feature is not complete until its runtime/MCP path is
    verified.
17. This README is the authoritative continuity checkpoint for future
    chats.

The recurring development sequence is:

``` text
Focused test
    ↓
Implementation
    ↓
Focused tests green
    ↓
Feature test group green
    ↓
Full regression green
    ↓
Runtime/MCP verification
    ↓
README checkpoint
    ↓
Git commit + push
```

------------------------------------------------------------------------

# 3. Architecture

``` text
                         QA MCP Server
                              │
                              ▼
                        MCP Tool Layer
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
  QA Workflows         Project Context       External Services
        │                     │                     │
        │                     ▼              ┌──────┴──────┐
        │               SQLite Repos         │             │
        │                                   Jira        GitHub
        │                                    │             │
        │                               JiraService   GitHubService
        │                                    │             │
        │                               JiraClient    GitHubClient
        │                              /      \        /      \
        │                            Mock    Cloud   Mock    Cloud
        │
        ├── Requirement Analyzer
        ├── Test Case Generator
        └── Test Case Reviewer
```

Layer responsibilities:

``` text
models/          Domain/data schemas
core/            Business/application services and factories
infrastructure/  Repositories and external clients
tools/           QA workflows
server.py        MCP transport and tool registration
```

------------------------------------------------------------------------

# 4. Repository Structure

``` text
src/qa_mcp/
├── core/
│   ├── config.py
│   ├── llm.py
│   ├── import_export/
│   ├── github/
│   │   ├── __init__.py
│   │   ├── factory.py
│   │   └── service.py
│   ├── jira/
│   │   ├── __init__.py
│   │   ├── factory.py
│   │   └── service.py
│   ├── project/
│   └── versioning/
├── infrastructure/
│   ├── github/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── mock_client.py
│   │   └── cloud_client.py
│   ├── jira/
│   │   ├── client.py
│   │   ├── mock_client.py
│   │   └── cloud_client.py
│   ├── project_repository.py
│   ├── sqlite_project_repository.py
│   └── versioning/
├── models/
│   └── schemas.py
├── tools/
└── server.py

tests/
data/qa_mcp.db
```

------------------------------------------------------------------------

# 5. Requirements

Current `requirements.txt`:

``` text
mcp
pydantic
pydantic-settings
PyYAML
python-dotenv
boto3
pytest
requests
```

Python 3.12 is the current development environment.

`requests` is required by the GitHub Cloud REST client.

------------------------------------------------------------------------

# 6. Initial Setup

``` bash
git clone https://github.com/sanumenon/qa-mcp.git
cd qa-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Current baseline:

``` text
111 passed, 1 warning
```

------------------------------------------------------------------------

# 7. `.env` Configuration --- IMPORTANT

The application loads `.env` from the project root.

The real `.env` must **never be committed**.

`.gitignore` excludes:

``` text
.env
.env.local
```

Create locally:

``` bash
touch .env
```

## Complete `.env` template

Use this template and replace the placeholder values locally:

``` dotenv
# ---------------------------------------------------------
# LLM
# ---------------------------------------------------------
LLM_PROVIDER=mock

# ---------------------------------------------------------
# Jira
# ---------------------------------------------------------
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email
JIRA_API_TOKEN=your-token

# ---------------------------------------------------------
# GitHub
# ---------------------------------------------------------
GITHUB_URL=https://api.github.com
GITHUB_TOKEN=your-github-token
GITHUB_OWNER=your-github-username-or-org
```

All values above are placeholders.

Never put real credentials into README or source control.

Verify `.env` is ignored:

``` bash
git check-ignore .env
```

------------------------------------------------------------------------

# 8. Feature Flags

Default `config/settings.yaml` keeps external connectors disabled:

``` yaml
features:
  requirement_analyzer: true
  testcase_generator: true
  testcase_reviewer: true
  jira_connector: false
  github_connector: false
  automation_generator: false
```

Therefore a fresh clone runs without Jira or GitHub access.

------------------------------------------------------------------------

# 9. Configuration Loading

``` text
.env
  ↓
load_config()
  ↓
environment variables override YAML
  ↓
application configuration
```

Supported connector variables:

``` text
JIRA_URL
JIRA_EMAIL
JIRA_API_TOKEN

GITHUB_URL
GITHUB_TOKEN
GITHUB_OWNER
```

------------------------------------------------------------------------

# 10. Jira Connector

Current architecture:

``` text
MCP
 │
 ▼
JiraService
 │
 ▼
JiraClient
 ├── MockJiraClient
 └── JiraCloudClient
```

The factory creates the service only when:

``` yaml
jira_connector: true
```

and all required values are non-empty after whitespace validation.

Read-only MCP tools:

``` text
get_jira_issue(issue_key)
search_jira_issues(jql, max_results=50)
```

Current real operations:

``` text
GET issue
JQL issue search
```

No Jira write operations are currently implemented.

Real Jira credentials are not required for unit tests.

------------------------------------------------------------------------

# 11. GitHub Connector

Current architecture:

``` text
MCP
 │
 ▼
GitHubService
 │
 ▼
GitHubClient
 ├── MockGitHubClient
 └── GitHubCloudClient
          │
          ▼
    GitHub REST API
```

The factory creates the service only when:

``` yaml
github_connector: true
```

and all three values are valid:

``` text
GITHUB_URL
GITHUB_TOKEN
GITHUB_OWNER
```

Whitespace-only values are rejected.

## Safe default

``` yaml
github_connector: false
```

means:

``` text
GitHub disabled
      ↓
github_service = None
      ↓
Server still starts
      ↓
No GitHub network access
```

Calling a GitHub MCP tool while disabled produces:

``` text
GitHub connector is not configured
```

## Current read-only GitHub MCP tools

``` text
get_github_repository(owner, repository)

get_github_issue(owner, repository, issue_number)

get_github_pull_request(owner, repository, pull_number)

search_github_issues(query, max_results=50)
```

No GitHub write operations are currently implemented.

## GitHub Cloud operations

``` text
GET repository
GET issue
GET pull request
GET /search/issues
```

Cloud-client tests mock HTTP requests, so real GitHub access is not
required.

------------------------------------------------------------------------

# 12. Project Context, Versioning and Import/Export

## Project context

``` text
QAProject
  │
  ├── Application
  ├── Environment
  ├── Requirements
  └── Test Suites
```

Duplicate project creation is rejected.

## Requirement versioning

``` text
Requirement V1
Requirement V2
Requirement V3
```

Requirements are immutable versions.

## Suite versioning

``` text
Requirement Version
        ↓
QA Suite Version
        ├── Test Cases
        └── Review
```

## Import/export

``` text
QA Project
    ↓
QAProjectExport
    ↓
JSON payload
    ↓
Import
```

Import validates the structure and protects against duplicate project
IDs.

------------------------------------------------------------------------

# 13. Current MCP Capabilities

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
```

------------------------------------------------------------------------

# 14. Running the Server

``` bash
python -m qa_mcp.server
```

Import verification:

``` bash
python -c "from qa_mcp.server import mcp; print('MCP Server import OK')"
```

GitHub integration verification:

``` bash
python -c "from qa_mcp.server import mcp; print('MCP GitHub integration import OK')"
```

Verify registered GitHub tools:

``` bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools() if 'github' in t.name])"
```

Expected:

``` text
['get_github_repository', 'get_github_issue', 'get_github_pull_request', 'search_github_issues']
```

------------------------------------------------------------------------

# 15. Testing Strategy

Every meaningful feature follows:

``` text
Configuration
    ↓
Client abstraction
    ↓
Mock client
    ↓
Service
    ↓
Cloud client
    ↓
Factory
    ↓
Runtime wiring
    ↓
MCP tools
    ↓
MCP registration
    ↓
Full regression
```

GitHub tests:

``` text
tests/test_github_config.py
tests/test_github_client.py
tests/test_github_mock_client.py
tests/test_github_service.py
tests/test_github_cloud_client.py
tests/test_github_factory.py
tests/test_github_tools.py
```

Run the GitHub suite:

``` bash
pytest -q \
 tests/test_github_config.py \
 tests/test_github_client.py \
 tests/test_github_mock_client.py \
 tests/test_github_service.py \
 tests/test_github_cloud_client.py \
 tests/test_github_factory.py \
 tests/test_github_tools.py
```

Current full regression:

``` bash
pytest -q
```

Result:

``` text
111 passed, 1 warning
```

------------------------------------------------------------------------

# 16. Known Warning

Current warning:

``` text
IncompleteFieldDefinitionWarning:
Field 'lifespan' has an incomplete definition
```

Source:

``` text
pydantic_settings
```

Policy:

-   known
-   non-blocking
-   does not fail tests
-   does not prevent MCP import
-   not caused by Jira or GitHub
-   do not suppress merely to make output clean
-   investigate separately if it becomes relevant

------------------------------------------------------------------------

# 17. SQLite Persistence

Database:

``` text
data/qa_mcp.db
```

Do not delete persistent databases merely to make tests pass.

Persistence-focused tests should use isolated database state.

------------------------------------------------------------------------

# 18. Security Rules

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
git check-ignore .env
```

Do not embed a personal access token in a Git remote URL.

Use:

``` text
https://github.com/sanumenon/qa-mcp.git
```

If a real token was ever exposed in a remote URL, revoke/rotate it.

------------------------------------------------------------------------

# 19. Git Checkpoint Procedure

After completing a phase/sub-step:

``` bash
pytest -q
git status
git diff
```

Review the changes and confirm no secrets are staged.

Then:

``` bash
git add .
git commit -m "Complete <checkpoint>"
git push
```

Verify:

``` bash
git status
git branch -vv
git log --oneline --decorate -10
```

Goal:

``` text
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

------------------------------------------------------------------------

# 20. Current Development Checkpoint

``` text
+-----------------------------------------------------------+
|                 QA MCP DEVELOPMENT CHECKPOINT             |
+-----------------------------------------------------------+
| Phase:             Phase 2                                |
| Capability:        GitHub Connector                       |
| Status:            COMPLETE through S6.9                 |
| Jira:              COMPLETE                               |
| GitHub:            COMPLETE through S6.9                 |
| Full regression:   111 passed                            |
| Warning:           1 known external warning              |
+-----------------------------------------------------------+
```

Verified:

``` text
GitHub configuration                 ✅
Client abstraction + models          ✅
Mock client                          ✅
Service                              ✅
Cloud/API client                     ✅
Factory                              ✅
Runtime wiring                       ✅
Read-only MCP tools                  ✅
Disabled connector safety            ✅
MCP registration                     ✅
Full regression                      ✅
```

------------------------------------------------------------------------

# 21. Milestone History

``` text
Phase 1
  |
  +-- Foundation
  +-- MCP
  +-- LLM abstraction
  +-- Requirement analysis
  +-- Test generation
  +-- Test review
  +-- QA suite workflow
  |
  v
Phase 1 COMPLETE
  |
  v
Phase 2
  |
  +-- S1 QA Project Context
  +-- S2 SQLite Persistence
  +-- S3 Requirement/Suite Versioning
  +-- S4 Import / Export
  +-- S5 Jira Connector
  +-- S6 GitHub Connector
  |
  v
CURRENT CHECKPOINT
```

------------------------------------------------------------------------

# 22. Phase 2 Roadmap

  Step   Capability                    Status
  ------ ----------------------------- -----------
  1      QA Project Context            COMPLETED
  2      SQLite Persistence            COMPLETED
  3      QA Suite Versioning           COMPLETED
  4      Import / Export               COMPLETED
  5      Jira Connector                COMPLETED
  6      GitHub Connector              COMPLETED
  7      Automation Case Generator     Planned
  8      QA Agent                      Planned
  9      CI/CD / broader integration   Planned
  10     Internet Deployment           Planned

The roadmap can be refined deliberately, but completed work must not be
recreated.

------------------------------------------------------------------------

# 23. Deliberately Not Implemented Yet

### Jira

``` text
create/update issues
comments
transitions
test-case publishing
Jira → QA end-to-end workflow
```

### GitHub

``` text
create/update issues
comments
pull request creation
pull request merge
repository writes
CI workflow mutation
```

### QA platform

``` text
automation code generation
QA agent/orchestrator
CI/CD execution
broader integrations
production deployment
```

Each future capability receives its own design, focused tests,
implementation, regression, and README checkpoint.

------------------------------------------------------------------------

# 24. Continuity / Handover Instructions

This README is the **authoritative development checkpoint** for
continuing QA MCP across chat sessions.

When starting a fresh session:

``` bash
cd qa-mcp
source .venv/bin/activate
git pull
pytest -q
git status
git log --oneline --decorate -10
```

Confirm:

``` text
111 passed, 1 warning
```

Then read this README and continue from the documented checkpoint.

## Fresh-chat handover statement

``` text
Resume QA MCP development from the GitHub/README checkpoint.

Phase 1 is complete.

Phase 2 completed:
- S1 Project Context
- S2 SQLite Persistence
- S3 Requirement & Suite Versioning
- S4 Import / Export
- S5 Jira Connector
- S6 GitHub Connector through S6.9

Current regression:
111 tests passing, 1 known non-blocking pydantic_settings warning.

Jira:
- read-only
- mock + Cloud clients
- factory
- runtime wiring
- MCP tools

GitHub:
- read-only
- mock + Cloud clients
- factory
- runtime wiring
- MCP tools
- disabled-without-credentials behavior verified
- MCP registration verified

Follow README development rules:
test-first, one step at a time, preserve architecture,
keep integrations mockable, never weaken tests, never commit secrets,
run full regression before closing a step, and update README at every
verified checkpoint.

Do not recreate completed Jira or GitHub work.
Read the repository and README first, verify pytest, then continue with
the next planned Phase 2 capability.
```

------------------------------------------------------------------------

# Final Reminder

This README is the **development checkpoint document**, not a substitute
for source code.

The repository, tests, configuration files, and Git history remain the
authoritative implementation sources.

When continuing development:

1.  Read this README.
2.  Verify Git status.
3.  Pull the latest checkpoint.
4.  Run the regression suite.
5.  Confirm the baseline.
6.  Inspect existing code before modifying it.
7.  Continue from the next documented development step.
8.  Follow the development guidelines.
9.  Update this README again at the next verified milestone.

**Current baseline: 111 passed, 1 warning.**

**Current completed connector milestone: Jira + GitHub read-only
integrations.**
