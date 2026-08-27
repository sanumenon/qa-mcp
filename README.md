# QA MCP

QA MCP is a Model Context Protocol (MCP) server for structured software-quality workflows.

The project is being developed incrementally using:

- layered architecture
- test-first implementation
- replaceable LLM providers
- persistent SQLite storage
- immutable QA versioning
- project import/export
- safe external connectors
- mockable infrastructure clients
- MCP tool registration only after runtime verification

> **Current checkpoint: Phase 2 — Slack Connector COMPLETE**
>
> **Current regression baseline: 143 passed**
>
> **Known warning: 1 non-blocking third-party `pydantic_settings` warning related to `lifespan`.**
>
> This README is the continuity checkpoint for future development. A fresh chat should read this document and inspect the repository before changing code.

---

# 1. Development Philosophy

The project is deliberately being built in small, verifiable checkpoints.

The standard development sequence is:

```text
Focused test
    ↓
Implementation
    ↓
Focused tests green
    ↓
Feature-group tests green
    ↓
Full regression green
    ↓
Runtime/MCP verification
    ↓
README checkpoint
    ↓
Git commit + push
```

## Non-negotiable development guidelines

1. Implement one phase/sub-step at a time.
2. Write focused tests before or alongside implementation.
3. Never weaken a test simply to make the suite green.
4. Preserve the layered architecture.
5. External integrations must remain mockable.
6. Never commit secrets or a real `.env`.
7. Keep MCP transport concerns out of core business logic.
8. Keep external API details inside infrastructure clients.
9. Keep persistence behind repository abstractions.
10. Keep LLM providers replaceable.
11. Validate AI output before downstream use.
12. Do not delete persistent databases merely to make tests pass.
13. Do not perform unrelated refactoring during feature work.
14. `pytest -q` is the authoritative regression check.
15. A feature is not complete until its runtime/MCP registration is verified.
16. Update this README at every major checkpoint.
17. Commit and push only after tests, runtime verification, documentation, and security checks are complete.

---

# 2. Current Development Status

## Phase 1 — Foundation

**Status: COMPLETE**

Implemented:

- MCP server foundation
- configuration loading
- LLM abstraction
- requirement analysis
- test-case generation
- test-case review
- QA-suite workflow

## Phase 2 — QA Platform Foundation

| Step | Capability | Status |
|---|---|---|
| P2-S1 | QA Project Context | COMPLETE |
| P2-S2 | SQLite Persistence | COMPLETE |
| P2-S3 | Requirement & Suite Versioning | COMPLETE |
| P2-S4 | Project Import / Export | COMPLETE |
| P2-S5 | Jira Connector | COMPLETE |
| P2-S6 | GitHub Connector | COMPLETE |
| P2-S7 | Slack Connector | COMPLETE |
| P2-S8 | Automation Case Generator | NEXT / PLANNED |

---

# 3. Completed Connector Checkpoints

## Jira

Completed:

```text
S5.1 Configuration
S5.2 Client Abstraction
S5.3 Service
S5.4 Cloud Client
S5.5 Read-only MCP Tools
S5.6 Configuration Wiring
S5.7 Controlled Integration Readiness
```

## GitHub

Completed:

```text
S6.1 Configuration
S6.2 Client Abstraction + Models
S6.3 Mock Client
S6.4 Service
S6.5 Cloud/API Client
S6.6 Factory
S6.7 Runtime Wiring
S6.8 Read-only MCP Tools + Disabled Safety
S6.9 MCP Registration + Regression
S6.10 README + Git Checkpoint
```

## Slack

Completed:

```text
S7.1 Configuration
S7.2 Client Abstraction + Models
S7.3 Mock Client
S7.4 Service
S7.5 Cloud Client
S7.6 Factory
S7.7 MCP Tools + Registration
S7.8 README + Git Checkpoint
```

**Do not recreate or redesign these completed connectors.**

---

# 4. Architecture

```text
                         QA MCP Server
                               │
                               ▼
                         MCP Tool Layer
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
    QA Workflows        Project Context      External Services
          │                    │                    │
          │                    ▼          ┌─────────┼─────────┐
          │              SQLite Repos      │         │         │
          │                              Jira      GitHub    Slack
          │                               │         │         │
          │                         JiraService    │   SlackService
          │                               │         │         │
          │                         JiraClient      │   SlackClient
          │                         /      \        │   /      \
          │                       Mock    Cloud     │ Mock     Cloud
          │                                      GitHub
          │
          ├── Requirement Analyzer
          ├── Test Case Generator
          ├── Test Case Reviewer
          └── QA Suite Workflow
```

The intended external-integration pattern is:

```text
MCP Tool
   ↓
Core Service
   ↓
Client Interface
   ├── Mock Client
   └── Cloud Client
```

This separation is intentional.

The service layer should not know HTTP endpoint details.

The MCP layer should not know external API implementation details.

---

# 5. Repository Structure

```text
qa-mcp/
│
├── config/
│   └── settings.yaml
│
├── data/
│   └── qa_mcp.db
│
├── src/
│   └── qa_mcp/
│       ├── core/
│       │   ├── config.py
│       │   ├── llm.py
│       │   ├── github/
│       │   │   ├── __init__.py
│       │   │   ├── factory.py
│       │   │   └── service.py
│       │   ├── jira/
│       │   │   ├── __init__.py
│       │   │   ├── factory.py
│       │   │   └── service.py
│       │   ├── slack/
│       │   │   ├── __init__.py
│       │   │   ├── factory.py
│       │   │   └── service.py
│       │   ├── import_export/
│       │   ├── project/
│       │   └── versioning/
│       │
│       ├── infrastructure/
│       │   ├── github/
│       │   │   ├── __init__.py
│       │   │   ├── client.py
│       │   │   ├── mock_client.py
│       │   │   └── cloud_client.py
│       │   ├── jira/
│       │   │   ├── __init__.py
│       │   │   ├── client.py
│       │   │   ├── mock_client.py
│       │   │   └── cloud_client.py
│       │   ├── slack/
│       │   │   ├── __init__.py
│       │   │   ├── client.py
│       │   │   ├── mock_client.py
│       │   │   └── cloud_client.py
│       │   ├── sqlite_project_repository.py
│       │   ├── project_repository.py
│       │   └── versioning/
│       │
│       ├── models/
│       │   └── schemas.py
│       ├── tools/
│       └── server.py
│
├── tests/
│   ├── test_jira_*.py
│   ├── test_github_*.py
│   └── test_slack_*.py
│
├── .env                 # local only, NEVER commit
├── .gitignore
├── README.md
└── requirements.txt
```

---

# 6. Environment Setup

```bash
git clone https://github.com/sanumenon/qa-mcp.git
cd qa-mcp

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Run the full suite:

```bash
pytest -q
```

Current verified result:

```text
143 passed, 1 warning
```

---

# 7. `.env` — REQUIRED LOCAL CONFIGURATION

The application loads `.env` from the project root using `python-dotenv`.

The real `.env` file must **never be committed**.

Create it locally:

```bash
touch .env
```

## Complete `.env` template

```dotenv
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

# ---------------------------------------------------------
# Slack
# ---------------------------------------------------------
SLACK_URL=https://slack.com/api
SLACK_TOKEN=your-slack-token
SLACK_DEFAULT_CHANNEL=your-channel
```

These are placeholders only.

Replace them with real values locally when using the actual external connectors.

**Never commit the populated `.env`.**

Verify:

```bash
git check-ignore .env
```

Environment variables override values in `config/settings.yaml`.

---

# 8. Default Feature Configuration

External connectors are intentionally disabled by default.

Current default feature configuration:

```yaml
features:
  requirement_analyzer: true
  testcase_generator: true
  testcase_reviewer: true
  jira_connector: false
  github_connector: false
  slack_connector: false
  automation_generator: false
```

A fresh clone therefore does not require live Jira, GitHub, or Slack credentials to run the normal test suite.

---

# 9. Configuration Loading

Current configuration flow:

```text
config/settings.yaml
        │
        ▼
     load_config()
        ▲
        │
       .env
        │
        ▼
environment variables override YAML
```

`src/qa_mcp/core/config.py` handles:

- YAML loading
- `.env` loading
- LLM provider override
- Jira environment overrides
- GitHub environment overrides
- Slack environment overrides

## Jira

```text
JIRA_URL
JIRA_EMAIL
JIRA_API_TOKEN
```

## GitHub

```text
GITHUB_URL
GITHUB_TOKEN
GITHUB_OWNER
```

## Slack

```text
SLACK_URL
SLACK_TOKEN
SLACK_DEFAULT_CHANNEL
```

---

# 10. Jira Connector

## Architecture

```text
MCP
 │
 ▼
JiraService
 │
 ▼
JiraClient
 ├── MockJiraClient
 └── JiraCloudClient
          │
          ▼
      Jira REST API
```

The Jira factory creates a service only when:

```yaml
jira_connector: true
```

and required credentials are present and non-whitespace.

## Current Jira MCP tools

```text
get_jira_issue(issue_key)

search_jira_issues(jql, max_results=50)
```

Current operations are read-only.

No Jira write operations have been implemented yet.

---

# 11. GitHub Connector

## Architecture

```text
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

Configuration:

```yaml
github:
  url: "https://api.github.com"
  token: ""
  owner: ""
```

Feature flag:

```yaml
github_connector: false
```

## Current GitHub MCP tools

```text
get_github_repository(owner, repository)

get_github_issue(owner, repository, issue_number)

get_github_pull_request(owner, repository, pull_number)

search_github_issues(query, max_results=50)
```

Current operations are read-only.

No repository writes, issue creation, PR creation, comments, merges, or workflow mutation have been implemented.

---

# 12. Slack Connector

## Architecture

```text
MCP
 │
 ▼
SlackService
 │
 ▼
SlackClient
 ├── MockSlackClient
 └── SlackCloudClient
          │
          ▼
      Slack Web API
```

Configuration:

```yaml
slack:
  url: "https://slack.com/api"
  token: ""
  default_channel: ""
```

Feature flag:

```yaml
slack_connector: false
```

When disabled:

```text
slack_connector: false
        ↓
create_slack_service()
        ↓
None
        ↓
server remains usable
```

No Slack network request is required for normal startup or tests when disabled.

## Slack client abstraction

The abstract client exposes:

```text
get_channel(channel)

get_messages(channel, limit=50)

search_messages(query, max_results=50)

get_thread(channel, thread_ts)
```

## Slack service

`SlackService` is deliberately thin.

It delegates to `SlackClient` and does not contain Slack HTTP/API details.

## Slack Cloud Client

The cloud client maps normalized operations to Slack Web API endpoints:

```text
get_channel()
    ↓
conversations.info

get_messages()
    ↓
conversations.history

search_messages()
    ↓
search.messages

get_thread()
    ↓
conversations.replies
```

Authentication uses the configured Slack bearer token.

Slack API errors are translated into application-level errors.

## Current Slack MCP tools

```text
get_slack_channel(channel)

get_slack_messages(channel, limit=50)

search_slack_messages(query, max_results=50)

get_slack_thread(channel, thread_ts)
```

Verified runtime registration:

```text
[
  'get_slack_channel',
  'get_slack_messages',
  'search_slack_messages',
  'get_slack_thread'
]
```

Current Slack operations are read-only.

Not implemented:

```text
send_message
reply_to_thread
create_channel
modify_channel
reactions
file_upload
Slack write workflows
```

---

# 13. Core QA Platform

## Project Context

```text
QAProject
  │
  ├── Application
  ├── Environment
  ├── Requirements
  └── Test Suites
```

## Requirement Versioning

Requirements are maintained as immutable versions:

```text
Requirement V1
      ↓
Requirement V2
      ↓
Requirement V3
```

## Suite Versioning

```text
Requirement Version
        ↓
QA Suite Version
        ├── Test Cases
        └── Review
```

## Import / Export

```text
QA Project
    ↓
QAProjectExport
    ↓
JSON
    ↓
Import
```

---

# 14. MCP Capabilities

## Core

```text
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
```

## Jira

```text
get_jira_issue
search_jira_issues
```

## GitHub

```text
get_github_repository
get_github_issue
get_github_pull_request
search_github_issues
```

## Slack

```text
get_slack_channel
get_slack_messages
search_slack_messages
get_slack_thread
```

---

# 15. Testing Strategy

Each external connector follows:

```text
Configuration
      ↓
Models + Client Interface
      ↓
Mock Client
      ↓
Service
      ↓
Cloud Client
      ↓
Factory
      ↓
Runtime Wiring
      ↓
MCP Tools
      ↓
MCP Registration
      ↓
Full Regression
```

## Jira tests

```text
tests/test_jira_config.py
tests/test_jira_client.py
tests/test_jira_service.py
tests/test_jira_cloud_client.py
tests/test_jira_factory.py
tests/test_jira_tools.py
```

## GitHub tests

```text
tests/test_github_config.py
tests/test_github_client.py
tests/test_github_mock_client.py
tests/test_github_service.py
tests/test_github_cloud_client.py
tests/test_github_factory.py
tests/test_github_tools.py
```

## Slack tests

```text
tests/test_slack_config.py
tests/test_slack_client.py
tests/test_slack_mock_client.py
tests/test_slack_service.py
tests/test_slack_cloud_client.py
tests/test_slack_factory.py
tests/test_slack_tools.py
```

Run the full regression:

```bash
pytest -q
```

Current verified result:

```text
143 passed, 1 warning
```

---

# 16. Runtime Verification

Import verification:

```bash
python -c "from qa_mcp.server import mcp; print('MCP Server import OK')"
```

Slack registration:

```bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools() if 'slack' in t.name])"
```

Expected:

```text
['get_slack_channel',
 'get_slack_messages',
 'search_slack_messages',
 'get_slack_thread']
```

GitHub registration:

```bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools() if 'github' in t.name])"
```

Runtime verification is part of feature completion.

---

# 17. Persistence

Current SQLite database:

```text
data/qa_mcp.db
```

Persistence is kept behind repository abstractions.

Do not delete persistent databases merely to make tests pass.

---

# 18. Security

Never commit:

```text
.env
real API tokens
real Slack tokens
real GitHub tokens
real Jira API tokens
passwords
AWS credentials
private keys
```

Before committing:

```bash
git status
git diff
git check-ignore .env
```

Never embed a personal access token in a Git remote URL.

Use:

```text
https://github.com/sanumenon/qa-mcp.git
```

If credentials are ever exposed in Git history or a remote URL, revoke/rotate them.

---

# 19. Known Warning

Current test output contains:

```text
IncompleteFieldDefinitionWarning:
Field 'lifespan' has an incomplete definition
```

from:

```text
pydantic_settings
```

This warning is:

- known
- non-blocking
- unrelated to Jira/GitHub/Slack
- not causing test failures
- not preventing MCP runtime import

Do not perform unrelated changes merely to eliminate this warning.

Current authoritative result:

```text
143 passed, 1 warning
```

---

# 20. Git Checkpoint Procedure

After a feature is complete:

```bash
pytest -q
git status
git diff
git check-ignore .env
```

Review all changed and untracked files.

Then:

```bash
git add .
git status
git commit -m "Complete <checkpoint>"
git push
```

Verify:

```bash
git status
git branch -vv
git log --oneline --decorate -10
```

Expected:

```text
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

---

# 21. Current Slack Checkpoint

The Slack connector is complete through S7.8.

```text
S7.1 Configuration                  ✅
S7.2 Client + Models                ✅
S7.3 Mock Client                    ✅
S7.4 Service                        ✅
S7.5 Cloud Client                   ✅
S7.6 Factory                        ✅
S7.7 MCP Tools + Registration      ✅
S7.8 Documentation Checkpoint      ✅
```

Slack-specific implementation includes:

```text
Configuration
Client
Mock Client
Service
Cloud Client
Factory
Tools
Runtime registration
```

Current full regression:

```text
143 passed, 1 warning
```

---

# 22. Phase 2 Checkpoint

The project now has three completed external read-only connectors:

```text
                    QA MCP
                       │
        ┌──────────────┼──────────────┐
        │              │              │
       Jira          GitHub         Slack
        │              │              │
     Service        Service        Service
        │              │              │
     Client         Client         Client
      /  \           /  \           /  \
   Mock Cloud     Mock Cloud     Mock Cloud
```

All three intentionally follow the same principles:

- configuration-driven
- disabled by default
- mockable
- service abstraction
- cloud/API isolation
- factory construction
- read-only MCP tools
- focused tests
- full regression
- runtime registration verification

This symmetry should be preserved for future integrations.

---

# 23. Roadmap

| Phase | Capability | Status |
|---|---|---|
| Phase 1 | QA MCP Foundation | COMPLETE |
| P2-S1 | Project Context | COMPLETE |
| P2-S2 | SQLite Persistence | COMPLETE |
| P2-S3 | Versioning | COMPLETE |
| P2-S4 | Import / Export | COMPLETE |
| P2-S5 | Jira | COMPLETE |
| P2-S6 | GitHub | COMPLETE |
| P2-S7 | Slack | COMPLETE |
| P2-S8 | Automation Case Generator | NEXT |
| Future | QA Agent / Orchestrator | PLANNED |
| Future | CI/CD integration | PLANNED |
| Future | Additional integrations | PLANNED |
| Future | Internet/production deployment | PLANNED |

---

# 24. Next Phase — Automation Case Generator

**Do not start by modifying Jira, GitHub, or Slack.**

The next capability should build on the existing QA platform.

Expected high-level direction:

```text
Requirement
     │
     ▼
Requirement Analyzer
     │
     ▼
Test Case Generator
     │
     ▼
Automation Case Generator
     │
     ├── automation framework
     ├── language
     ├── page/object information
     ├── locators
     ├── test data
     └── generated automation structure
```

The exact implementation must be determined from the current repository and existing design before code is changed.

Follow the established test-first sequence.

Do not assume requirements that have not yet been agreed.

---

# 25. Future Integration Direction

The completed connectors provide the foundation for a larger QA workflow.

Potential future direction:

```text
Jira Requirement
       │
       ▼
Requirement Analyzer
       │
       ▼
Test Case Generator
       │
       ▼
Automation Generator
       │
       ▼
GitHub
       │
       ▼
Slack Notification
       │
       ▼
QA Agent / Orchestrator
```

This is a future architectural direction, not current functionality.

Do not implement the complete orchestration until each capability and its interfaces are deliberately designed and tested.

---

# 26. Deliberately Not Implemented

## Jira

```text
create issue
update issue
comments
transitions
test-case publishing
end-to-end Jira → QA workflow
```

## GitHub

```text
create issue
update issue
comments
create pull request
merge pull request
repository writes
workflow mutation
```

## Slack

```text
send messages
reply to threads
create channels
modify channels
reactions
file uploads
write workflows
```

## QA Platform

```text
automation generation
QA agent/orchestrator
CI/CD execution
production deployment
internet deployment
```

These are deliberately deferred.

---

# 27. Fresh-Chat Continuity Instructions

When continuing this project in a new ChatGPT conversation:

## Step 1 — Read this README

This document is the primary continuity checkpoint.

## Step 2 — Inspect the actual repository

Run:

```bash
git status
git log --oneline --decorate -10
```

## Step 3 — Run the regression

```bash
pytest -q
```

Do not assume the README is newer than the actual code.

## Step 4 — Verify runtime registration when relevant

For example:

```bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools() if 'slack' in t.name])"
```

## Step 5 — Do not recreate completed work

Completed:

```text
Foundation
Project Context
SQLite Persistence
Versioning
Import / Export
Jira
GitHub
Slack
```

## Step 6 — Continue from the next checkpoint

Current next capability:

```text
P2-S8 — Automation Case Generator
```

unless the actual repository state shows that this has already changed.

## Step 7 — Preserve the development sequence

```text
test
→ implement
→ focused regression
→ full regression
→ runtime verification
→ README checkpoint
→ Git commit
→ Git push
```

## Step 8 — Avoid unrelated refactoring

Do not clean up unrelated code while implementing a focused phase.

---

# 28. Final Verified Checkpoint

```text
===========================================================
                 QA MCP CHECKPOINT
===========================================================

Phase 1 Foundation                    COMPLETE
Project Context                       COMPLETE
SQLite Persistence                    COMPLETE
Versioning                            COMPLETE
Import / Export                       COMPLETE
Jira Connector                       COMPLETE
GitHub Connector                     COMPLETE
Slack Connector                      COMPLETE

Current full regression:
                         143 PASSED

Known warning:
                         1 non-blocking
                         pydantic_settings warning

External connectors:
                         Jira    READ-ONLY
                         GitHub  READ-ONLY
                         Slack   READ-ONLY

Secrets:
                         .env remains local/ignored

Current next capability:
                         P2-S8
                         Automation Case Generator

Continuity:
                         This README is the
                         primary project checkpoint.

===========================================================
```

This README is intended to be sufficient for a fresh development session to understand what has been built, the architectural decisions already made, what has deliberately been deferred, the current test baseline, the environment configuration, and exactly where development should resume.
