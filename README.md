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

# 8. Project Structure

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

# 9. Local Setup

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
49 passed
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

# 10. Development Guidelines

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

# 11. Architectural Principles

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

# 12. Phase 2 Roadmap

| Step | Capability | Status |
|---|---|---|
| 1 | QA Project Context | COMPLETED |
| 2 | SQLite Persistence | COMPLETED |
| 3 | QA Suite Versioning | COMPLETED |
| 4 | Import / Export | COMPLETED |
| 5 | Jira Connector | NEXT |
| 6 | Jira → QA Workflow | Planned |
| 7 | Automation Case Generator | Planned |
| 8 | QA Agent | Planned |
| 9 | GitHub / CI Integration | Planned |
| 10 | Internet Deployment | Planned |

---

# 13. Planned Final Architecture

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

# 14. Current Baseline

```text
Phase 1
  Steps 1–7  COMPLETED

Phase 2
  Step 1 — QA Project Context       COMPLETED
  Step 2 — SQLite Persistence       COMPLETED
  Step 3 — QA Suite Versioning      COMPLETED
  Step 4 — Import / Export          COMPLETED
```

Current verification:

```text
49 tests passed
SQLite persistence verified
Requirement versioning verified
Suite versioning verified
Import/export contract verified
Import validation verified
Round-trip persistence verified
MCP import/export verified
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

---

# 15. Next Development Step

```text
Phase 2 → Step 5
       |
       v
Jira Connector
```

The next phase of implementation should begin only after this README checkpoint has been retained.

---

# 16. Milestone History

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
  |
  v
Phase 2 Step 4 COMPLETE
```

This README represents the project state after successful verification of **Phase 2 → Step 4 — Import / Export**.
