# QA MCP Server

An extensible Model Context Protocol (MCP) server designed to become a unified AI-powered QA platform.

## Current Status

### Phase 1 — Foundation & QA Intelligence

**COMPLETED**

| Step | Capability | Status |
|---|---|---|
| 1 | Project foundation | COMPLETED |
| 2 | MCP server + health | COMPLETED |
| 3 | LLM provider abstraction | COMPLETED |
| 4 | Requirement Analyzer | COMPLETED |
| 5 | Test Case Generator | COMPLETED |
| 6 | Test Case Reviewer | COMPLETED |
| 7 | End-to-End QA Workflow | COMPLETED |

### Phase 2 — Project Context, Persistence, Versioning & Portability

| Step | Capability | Status |
|---|---|---|
| 1 | QA Project Context | COMPLETED |
| 2 | SQLite Persistence | COMPLETED |
| 3 | QA Suite Versioning | COMPLETED |
| 4 | Import / Export | COMPLETED |
| 5 | Jira Connector | COMPLETED |

---

# 1. Vision

The long-term goal is to build a reusable QA MCP platform exposing QA capabilities to MCP-compatible AI clients.

```text
MCP Client / AI Assistant
          |
          v
      QA MCP Server
          |
   +------+------+------+
   |             |      |
   v             v      v
QA Intelligence Connectors Automation
   |             |      |
Analyze        Jira    UI
Generate       GitHub  API
Review         Slack   Mobile
                       Performance
          |
          v
       QA Agent
          |
          v
 Persistent QA Context
          |
          v
 Project / Requirement / Suite Versions
          |
          v
 Import / Export
```

---

# 2. Phase 1 Architecture

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

Core MCP capabilities:

```text
analyze_requirement
generate_test_cases
review_test_cases
generate_qa_suite
```

---

# 3. LLM Architecture

```text
LLMProvider
     |
     +---- MockLLM
     |
     +---- BedrockLLM
```

LLM access is provider-independent so the QA tools can be tested locally and later connected to AWS Bedrock or another provider.

AI output is validated using Pydantic models before downstream processing.

---

# 4. Phase 2 Step 1 — QA Project Context

**Status: COMPLETED**

A QA project contains:

```text
QAProject
 |
 +-- project_id
 +-- name
 +-- description
 +-- application
 +-- environment
 +-- metadata
```

Core service:

```text
ProjectContext
 |
 +-- create_project()
 +-- get_project()
```

MCP tools:

```text
create_qa_project
get_qa_project
```

---

# 5. Phase 2 Step 2 — SQLite Persistence

**Status: COMPLETED**

Projects are persisted in:

```text
data/qa_mcp.db
```

SQLite table:

```text
qa_projects
```

Architecture:

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

The core context does not depend directly on SQLite.

Persistence was verified across separate Python processes.

---

# 6. Phase 2 Step 3 — QA Suite Versioning

**Status: COMPLETED**

QA requirements and generated suites are versioned and persisted independently.

## Requirement versions

```text
QA Project
   |
   +-- Requirement v1
   +-- Requirement v2
   +-- Requirement v3
```

Each requirement version contains:

- `version_id`
- `project_id`
- `version`
- `requirement`
- `application`
- `environment`
- `created_at`

Versions are maintained independently per project.

## Suite versions

Each suite records the requirement version that produced it:

```text
Requirement v1
      |
      v
Suite v1

Requirement v2
      |
      v
Suite v2
```

Each suite version contains:

- `suite_id`
- `project_id`
- `requirement_version_id`
- `version`
- `test_cases`
- `review`
- `created_at`

## Architecture

```text
core/
└── versioning/
    └── service.py
        |
        v
infrastructure/
└── versioning/
    ├── repositories.py
    └── sqlite_version_repository.py
        |
        v
      SQLite
```

The two `versioning` folders are intentional:

- `core/versioning` contains business logic.
- `infrastructure/versioning` contains repository interfaces and SQLite implementations.

## Core services

```text
QARequirementVersioningService
QASuiteVersioningService
```

## Repository interfaces

```text
RequirementVersionRepository
SuiteVersionRepository
```

## SQLite implementations

```text
SQLiteRequirementVersionRepository
SQLiteSuiteVersionRepository
```

## MCP tools

Requirement:

```text
create_requirement_version
get_requirement_version
list_requirement_versions
```

Suite:

```text
create_suite_version
get_suite_version
list_suite_versions
```

---

# 7. Phase 2 Step 4 — Import / Export

**Status: COMPLETED**

The QA MCP server now supports portable project artifacts containing:

```text
QA Project
    |
    +-- Requirement Versions
    |
    +-- Suite Versions
```

## Export

The export flow is:

```text
SQLite
   |
   +-- Project
   +-- Requirement Versions
   +-- Suite Versions
           |
           v
QAImportExportService
           |
           v
QAProjectExport
           |
           v
JSON
```

Export is based on persisted data, not caller-assembled objects.

MCP tool:

```text
export_qa_project
```

Input:

```text
project_id
```

Output:

```text
{
    "project_id": "...",
    "export_version": "1.0",
    "payload": "..."
}
```

## Import

The import flow is:

```text
JSON
  |
  v
Parse
  |
  v
QAProjectExport validation
  |
  v
Relationship validation
  |
  v
Duplicate project check
  |
  v
SQLite persistence
```

MCP tool:

```text
import_qa_project
```

Import validates:

- Export JSON
- Export structure
- Project identity
- Requirement → project relationship
- Suite → project relationship
- Suite → requirement-version relationship
- Duplicate project protection

Existing projects are **not silently overwritten**.

## Round-trip verification

The complete round trip has been verified:

```text
SQLite DB A
    |
    v
EXPORT
    |
    v
JSON
    |
    v
IMPORT
    |
    v
SQLite DB B
    |
    v
Compare
```

Verified artifacts:

```text
Project           ✅
Requirements      ✅
Suites            ✅
Relationships     ✅
```

## Test isolation

MCP import/export tests use isolated temporary SQLite databases.

This prevents test execution from polluting:

```text
data/qa_mcp.db
```

and allows repeated test execution without relying on previous test state.

## P2-S4 verification baseline

```text
Import/Export focused tests: 7 passed
MCP Import/Export tests:     2 passed
Full regression:            49 passed
Application-code warnings:   0
Known external warning:      1
```

The remaining warning is the known external `pydantic_settings` warning concerning the `lifespan` field's unresolved forward reference.

---


# 8. Phase 2 Step 5 — Jira Connector

**Status: COMPLETED**

The QA MCP server now has a Jira integration layer designed to remain usable without Jira access.

The connector is intentionally read-only at this stage.

## Jira architecture

```text
MCP Jira Tools
      |
      v
 JiraService
      |
      v
 JiraClient
   /      \
  v        v
Mock      Cloud
Client    Client
            |
            v
       Jira Cloud REST API
```

The architecture keeps Jira-specific transport and authentication outside the core QA business logic.

## Jira configuration

Jira is disabled by default:

```yaml
features:
  jira_connector: false
```

The default Jira configuration in:

```text
config/settings.yaml
```

is:

```yaml
jira:
  url: ""
  email: ""
  api_token: ""
```

Environment variables override these values.

### Required `.env` variables

Create a `.env` file in the **repository root**:

```text
qa-mcp/
├── .env
├── config/
├── src/
├── tests/
└── README.md
```

Use the following template:

```dotenv
# LLM
LLM_PROVIDER=mock

# Jira Cloud
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-token
```

Replace the placeholder values with the values supplied by your organisation.

**Important:**

- `JIRA_URL` is your Jira Cloud base URL.
- `JIRA_EMAIL` is the Jira account email used for API authentication.
- `JIRA_API_TOKEN` is the Jira Cloud API token.
- Never commit the real `.env` file.
- Never put the real Jira API token in `config/settings.yaml`.
- Never put a real token into tests.
- `.env` and `.env.local` are already excluded by `.gitignore`.

For a developer who does not have Jira access yet, leave the Jira values empty and keep:

```yaml
jira_connector: false
```

The application and test suite are designed to continue working in this mode.

## Jira configuration flow

```text
.env
  |
  | JIRA_URL
  | JIRA_EMAIL
  | JIRA_API_TOKEN
  v
load_config()
  |
  v
config["jira"]
  |
  v
create_jira_service()
  |
  +------------------------------+
  |                              |
  | jira_connector = false       | valid configuration
  | or missing credentials       |
  v                              v
No Jira service              JiraService
                                  |
                                  v
                           JiraCloudClient
```

The Jira factory also rejects whitespace-only credentials so invalid configuration does not accidentally activate the connector.

## Jira client abstraction

The core abstraction is:

```text
JiraClient
├── get_issue()
└── search_issues()
```

This allows tests to use a mock implementation without making network calls.

## Normalized Jira models

Jira responses are normalized into:

```text
JiraIssue
JiraSearchResult
```

`JiraIssue` contains fields including:

```text
key
summary
description
issue_type
status
priority
project_key
project_name
assignee
reporter
url
```

## Current Jira MCP tools

### Get a Jira issue

```text
get_jira_issue(issue_key)
```

### Search Jira issues

```text
search_jira_issues(jql, max_results=50)
```

These operations are currently **read-only**.

The following operations are deliberately not part of the current Jira scope:

```text
Create issue
Update issue
Add comment
Transition issue
Delete issue
```

They may be considered in a later phase only after the read-only integration is stable.

## Jira without Jira access

Real Jira credentials are **not required** to develop or test QA MCP.

The project supports:

```text
Local development
      |
      v
Mock Jira Client
      |
      v
No external Jira dependency
```

When real configuration is available:

```text
Jira enabled
      |
      v
JiraCloudClient
      |
      v
Jira Cloud
```

No Jira network call is required by the automated test suite.

## Jira verification

Jira-focused tests currently verify:

```text
Configuration                 OK
Environment loading          OK
Client abstraction           OK
Jira service                 OK
Cloud client                 OK
Factory                      OK
Read-only MCP tools          OK
Whitespace credential guard  OK
```

Current Jira-focused baseline:

```text
28 passed
```

---

# 17. Project Structure

Current important source structure:

```text
qa-mcp/
|
+-- src/
|   +-- qa_mcp/
|       |
|       +-- core/
|       |   +-- config.py
|       |   +-- llm.py
|       |   +-- project/
|       |   |   +-- context.py
|       |   |
|       |   +-- versioning/
|       |   |   +-- service.py
|       |   |
|       |   +-- import_export/
|       |       +-- service.py
|       |
|       +-- infrastructure/
|       |   +-- project_repository.py
|       |   +-- sqlite_project_repository.py
|       |   |
|       |   +-- versioning/
|       |       +-- repositories.py
|       |       +-- sqlite_version_repository.py
|       |
|       +-- models/
|       |   +-- schemas.py
|       |
|       +-- tools/
|       |   +-- requirement/
|       |   +-- testcase/
|       |   +-- workflow/
|       |
|       +-- server.py
|
+-- tests/
+-- config/
+-- data/
|   +-- qa_mcp.db
|
+-- README.md
```

---

# 17. Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run tests:

```bash
pytest -q
```

Current verified baseline:

```text
77 passed, 1 warning
```

Run the MCP server:

```bash
python -m qa_mcp.server
```

Verify server imports:

```bash
python -c "from qa_mcp.server import mcp; print('MCP server imports OK')"
```

---

# 17. Development Guidelines

We follow this workflow for every implementation step:

```text
IMPLEMENT
    |
    v
FOCUSED TESTS
    |
    v
FULL REGRESSION
    |
    v
RUNTIME / MCP VERIFICATION
    |
    v
FIX / REFINE
    |
    v
MARK STEP COMPLETE
    |
    v
UPDATE README
    |
    v
DOWNLOAD NEW README CHECKPOINT
    |
    v
NEXT STEP
```

Rules:

1. Implement one step at a time.
2. Test every feature.
3. Existing tests must remain green.
4. No step is complete until locally verified.
5. Update README at every verified milestone.
6. Core business logic must remain independent of MCP transport.
7. Persistence and external integrations stay behind interfaces.
8. LLM providers remain replaceable.
9. AI output must be validated.
10. Tests must remain repeatable against persistent storage.
11. Do not delete persistent databases merely to make tests pass.
12. Use isolated databases for persistence-focused tests.
13. Do not manually copy assistant conversation into README.
14. The README is the authoritative development checkpoint.
15. No major feature is complete until its MCP/runtime path is verified.

---

# 17. Architectural Principles

1. **Core business logic belongs in `core`.**
2. **Persistence belongs in `infrastructure`.**
3. **MCP transport belongs in `server.py` and MCP-facing tools.**
4. **Domain/data models belong in `models`.**
5. **Core services must not depend directly on SQLite implementations.**
6. **External integrations must be isolated behind interfaces.**
7. **LLM providers remain replaceable.**
8. **AI-generated output must be validated before downstream use.**
9. **Persistent data must not be confused with test fixtures.**
10. **Tests must be repeatable.**
11. **Import operations must validate relationships before persistence.**
12. **Imports must not silently overwrite existing projects.**
13. **Completed milestones require regression verification.**
14. **README updates are part of milestone completion.**

---

# 17. Phase 2 Roadmap

| Step | Capability | Status |
|---|---|---|
| 1 | QA Project Context | COMPLETED |
| 2 | SQLite Persistence | COMPLETED |
| 3 | QA Suite Versioning | COMPLETED |
| 4 | Import / Export | COMPLETED |
| 5 | Jira Connector | COMPLETED |
| 5 | Jira Connector | COMPLETED |
| 6 | Jira → QA Workflow | Planned |
| 7 | Automation Case Generator | Planned |
| 8 | QA Agent | Planned |
| 9 | GitHub / CI Integration | Planned |
| 10 | Internet Deployment | Planned |

---

# 17. Planned Final Architecture

```text
                    MCP CLIENT / AI ASSISTANT
                              |
                              v
                       +-------------+
                       |   QA MCP    |
                       |   Server    |
                       +------+------+
                              |
              +---------------+----------------+
              |               |                |
              v               v                v
        QA Intelligence   Connectors      Automation
              |               |                |
        +-----+-----+     +---+---+       +----+----+
        |     |     |     |   |   |       |    |    |
     Analyze Gen  Review Jira GitHub    UI   API  Perf
                                            Mobile
              |
              v
          QA Agent
              |
              v
       Persistent Context
              |
              v
     Project / Requirement
        / Suite Versions
              |
              v
       Import / Export
```

---

# 17. Current Baseline

```text
Phase 1
  Steps 1–7  COMPLETED

Phase 2
  Step 1 — QA Project Context       COMPLETED
  Step 2 — SQLite Persistence       COMPLETED
  Step 3 — QA Suite Versioning      COMPLETED
  Step 4 — Import / Export          COMPLETED
  Step 5 — Jira Connector           COMPLETED
```

Current verification:

```text
77 tests passed
SQLite persistence verified
Requirement versioning verified
Suite versioning verified
Import/export contract verified
Import validation verified
Round-trip persistence verified
MCP import/export verified
Jira configuration verified
Jira client abstraction verified
Jira service verified
Jira Cloud client verified
Jira factory verified
Jira read-only MCP tools verified
Jira offline/mock path verified
Jira credential validation verified
MCP server imports successfully
Test isolation verified
```

Known warning:

```text
pydantic_settings
IncompleteFieldDefinitionWarning
Field 'lifespan'
```

This is an external dependency warning and is not currently blocking functionality or tests.

Current warning policy:

```text
Do not hide the warning merely to obtain clean test output.
Investigate separately if it becomes relevant.
```

---

# 15. Current Development Checkpoint

```text
+------------------------------------------------------+
|              QA MCP DEVELOPMENT CHECKPOINT           |
+------------------------------------------------------+
| Phase:        Phase 2                                |
| Step:         Step 5 — Jira Connector                |
| Status:       COMPLETED                              |
| Jira tests:   28 passed                              |
| Full tests:   77 passed                              |
| Warning:      1 known external warning               |
+------------------------------------------------------+
```

The repository is safe to continue without Jira credentials.

The real Jira configuration can be enabled later by:

1. Creating `.env`.
2. Filling `JIRA_URL`.
3. Filling `JIRA_EMAIL`.
4. Filling `JIRA_API_TOKEN`.
5. Setting `jira_connector: true`.
6. Running the regression suite.
7. Performing a controlled real Jira connectivity verification when organisation access is available.

---

# 16. Next Development Step

```text
Phase 2
   |
   v
Step 5 — Jira Connector
   |
   | COMPLETE
   v
Next planned Phase 2 capability
```

Before starting the next step:

```bash
git pull
source .venv/bin/activate
pytest -q
```

The expected baseline is:

```text
77 passed, 1 warning
```

Do not restart Jira implementation. Continue from this checkpoint.

---

# 19. Milestone History

```text
Phase 1
  |
  +-- Foundation
  +-- LLM abstraction
  +-- Requirement analysis
  +-- Test generation
  +-- Test review
  +-- QA suite workflow
  +-- MCP integration
  |
  v
Phase 1 COMPLETE

Phase 2
  |
  +-- QA Project Context
  +-- SQLite Persistence
  +-- Requirement/Suite Versioning
  +-- Import / Export
  +-- Jira Connector
  |
  v
Phase 2 Step 5 COMPLETE
```

This README represents the project state after successful verification of **Phase 2 → Step 4 — Import / Export**.


---

# 20. Continuity / Handover Instructions

This README is the **authoritative development checkpoint** for continuing QA MCP development across sessions.

When starting a new development session:

```text
1. Read README.md
2. Check Git status
3. Pull the latest checkpoint
4. Activate .venv
5. Run pytest -q
6. Confirm the baseline
7. Continue from "Next Development Step"
```

Recommended commands:

```bash
git status
git pull
source .venv/bin/activate
pytest -q
```

If the baseline is different from the documented checkpoint, stop and investigate before implementing new functionality.

## Current handover state

```text
Phase 1                              COMPLETE
Phase 2 / Step 1                     COMPLETE
Phase 2 / Step 2                     COMPLETE
Phase 2 / Step 3                     COMPLETE
Phase 2 / Step 4                     COMPLETE
Phase 2 / Step 5                     COMPLETE

Current regression                   77 passed
Known external warnings              1
Real Jira credentials required       NO
Real Jira integration tested         NOT YET
```

The Jira connector is architecturally ready, but organisation-specific Jira credentials and a controlled live connectivity check are intentionally separate from the automated test baseline.

At every future milestone, update this README with:

```text
- phase and step
- implementation status
- architecture changes
- diagrams where useful
- setup/configuration changes
- environment variables
- focused test count
- full regression count
- known warnings
- next development step
```

This prevents the development context from being lost when work resumes in a later chat or environment.
