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

**Current implementation checkpoint:** P2-S9.17 — Internal Identity, Project Authorization, and Execution Credential Isolation

**P2-S9.17 status:** COMPLETE — committed as `5759211` and `f94f05c`, pushed to `origin/main`.

**Current Git base:** `f94f05c` — Fix local development operator access (corrective commit for P2-S9.17). This commit is on `main` and `origin/main`.

**Approved product direction:** Model B — Internal QA-Team Platform

**Latest committed checkpoint:** P2-S9.17 — Internal Identity, Project Authorization, and Execution Credential Isolation, committed as `5759211` (implementation) and `f94f05c` (local development operator correction), pushed to `origin/main`.

**Repository:** `https://github.com/sanumenon/qa-mcp`

**Branch:** `main`

**Historical P2-S9.15 verification baseline:**

- Focused artifact/workspace/history/API tests: **30 passed**
- Focused artifact-review/execution browser test: **1 passed**
- Full regression: **329 passed**
- Warnings: **8**
- Failures: **0**
- `git diff --check`: clean
- Project Workspace two-artifact review and execution browser verification: **passed**
- Existing artifact response shape, API/MCP fields, persistence schema, and execution behavior preserved
- P2-S9.15 is committed as `ba9e27c` and pushed to `origin/main`

## Latest verified implementation notes

### Bedrock test-case generation hardening

- Commit `9e5f8f7` normalizes a valid single test-case object into the required
  `{"test_cases": [...]}` response wrapper.
- Commit `70d1f8f` increases the Bedrock `maxTokens` configuration from `4096`
  to `12000`.
- The full regression suite remains green after both changes.
- A single test-case response is accepted only when it matches the valid
  test-case schema; unrelated or incomplete payloads remain errors.
- The generation prompt already requires comprehensive coverage of positive,
  negative, and edge scenarios.
- Runtime verification has now confirmed that Bedrock returns a complete
  multi-case suite.

### Bedrock runtime timeout resolution

The remaining runtime failure was not caused by guardrails or incomplete
test-case parsing.

The actual production failure was a Bedrock `ReadTimeoutError` caused by the
default **60-second read timeout**. Real test-case generation could exceed
that duration.

The production Bedrock configuration was hardened to:

- Connect timeout: **60 seconds**
- Read timeout: **180 seconds**
- Retry mode: **standard**
- Maximum attempts: **1**

The configuration supports environment-variable overrides for these values.

A real diagnostic run using the hardened configuration completed successfully
and generated a multi-case suite. Scenario-batched generation was therefore
**not required to resolve this timeout blocker**.

### QA suite completeness verification

The live Customer Portal QA-suite endpoint was verified using the actual
`QASuiteWorkspaceRequest` contract.

The successful runtime verification returned:

- HTTP status: **200**
- `test_cases` response: wrapped object
- Generated test cases: **50**
- First ID: **TC001**
- Last ID: **TC050**

An earlier live verification also produced **60 test cases**, confirming that
the generated collection is not limited to a single test case. The exact count
may vary with the LLM response.

The established backend contract remains:

```text
test_cases
└── test_cases[]
```

No backend API contract was changed.

## Completed capabilities

The following capabilities are implemented and verified:

1. Persistent project QA workspace.
2. Requirement analysis and test-case generation.
3. Test-case selection using Select All and Clear All.
4. Selective QA-suite persistence.
5. QA-suite version feedback after successful persistence.
6. Automation test-case generation.
7. Executable Playwright code generation.
8. Automation execution service.
9. Execution history persistence.
10. Execution result review.
11. Environment-independent Playwright URL handling.
12. `BASE_URL` injection into generated automation execution.
13. Configurable execution timeout.
14. Configurable automation workspace root.
15. Configurable workspace retention.
16. Controlled environment-variable propagation.
17. Hardened automation execution configuration.
18. Focused and full regression coverage for the completed implementation.

## Current implementation boundary

P2-S9.14-B adds project-scoped execution metrics and recent failure review to
the existing Project QA Workspace. P2-S9.14-C adds read-only review of
generated automation artifacts in that workspace, reusing artifact data
already returned by the workspace API. P2-S9.14-D adds read-only review of
persisted test case details from the existing project workspace response.
Review remains separate from candidate selection, artifact review, and
execution. The global Execution and Reports pages and all backend contracts
remain unchanged.

## P2-S9.16 — Project-Centric QA Workspace UX

**Status: COMPLETE AND APPROVED — committed as `6b8c532` and pushed to `origin/main`**

The approved deployment direction remains Model B — a trusted internal QA
team. P2-S9.16 organizes the existing Project QA Workspace into these areas:

- Overview
- Requirements
- Test Cases
- Automation
- Executions
- Reports

The workspace carries project context through the existing `project_id`.
Overview metrics and recent failure information derive from existing workspace,
reporting, and failure-analysis data. The Requirements area retains the
existing QA-suite generation, generated-case review and selection, and
selective-save workflow. Client-side testcase search and filtering use
persisted fields already returned by the workspace API.

P2-S9.16 preserves the explicit separation between Review and Execute and
safe, inert rendering. It includes responsive layout and accessibility
improvements. Existing API and MCP contracts, persistence behavior, database
schema, and execution behavior are unchanged.

### Validation

```text
Focused web tests:                 30 passed, 1 warning
Full regression suite:             329 passed, 8 warnings, 0 failures
JavaScript syntax checks:           passed
git diff --check:                    clean
Project Workspace browser flow:    passed
```

Browser verification covered project navigation and overview metrics,
generated and persisted test-case review, search/filter and selection/save,
inert rendering, automation candidate selection, artifact review, explicit
execution, execution history and insights, and empty states. JavaScript syntax
checks completed. API/MCP contracts, persistence/database schema, and execution
behavior remain unchanged. The implementation is complete and approved,
committed as `6b8c532`, and pushed to `origin/main`.

P2-S9.16 does not claim internal network deployment readiness. Model B
readiness still requires decisions about identity/access and SQLite
backup/recovery. Execution remains a local subprocess and is not a sandbox.
Model C network exposure and Model D untrusted execution remain out of scope.

## P2-S9.17 — Internal Identity, Project Authorization, and Execution Credential Isolation

**Status: COMPLETE**

**Implementation commit:** `5759211` — Complete P2-S9.17 internal identity and authorization

**Corrective commit:** `f94f05c` — Fix local development operator access (ensures configured development subject maps to trusted LOCAL_OPERATOR identity)

The selected identity provider is Google Workspace using Google OAuth 2.0 / OpenID Connect. Google client credentials, redirect URI, and Workspace domain are deployment settings; the Workspace domain is not hard-coded. Production startup requires Google OIDC configuration, a 32-character session secret, an HTTPS redirect URI, and Secure session cookies. The local development actor is configuration-controlled and is rejected in production.

### Identity and project access

- Authlib validates Google OIDC discovery issuer, ID-token signature against Google JWKS, audience, expiry, and nonce. QA-MCP accepts only a verified email and the configured Google `hd` Workspace domain. The stable Google `sub` is the actor key; access/ID tokens are not stored in the application session or exposed to browser JavaScript.
- Signed, HttpOnly, SameSite=Lax sessions carry the verified subject/email and expiry. Browser state-changing requests use a session-bound CSRF token.
- The minimal roles are `global_admin` (configured Google subjects) and project-scoped `project_member`. A new project's creator receives membership. Global admins provision additional memberships through the protected project-membership API.
- The versioned SQLite migration adds membership and security-audit tables transactionally without rebuilding existing tables. `QA_LEGACY_PROJECT_OWNERS` explicitly maps legacy project IDs to Google subject IDs. Unmapped legacy projects are denied to members and counted in readiness; there is no default-wide grant.
- Project authorization is enforced in shared project, versioning, workspace, and import/export services. Suite creation rejects a requirement version from a different project. Non-admin users receive project-filtered global execution/history/report/failure results.

### Execution, MCP, and operations

- Generated automation receives only the explicit runtime allowlist (`PATH`, `HOME`, temporary-directory/locale variables, `PLAYWRIGHT_BROWSERS_PATH`, `CI`, `SYSTEMROOT`) plus configured `BASE_URL`. Application/provider credentials and arbitrary inherited variables are excluded.
- MCP remains trusted-local stdio only. Local stdio calls use the explicit local-operator trust boundary; Google browser authentication does not confer MCP access. The `analyze_automation_failures` registration now occurs before the stdio server starts, and the launched process inventory is verified.
- `/health/live` reports process liveness. `/api/ready` checks the database and reports when legacy project ownership mapping remains outstanding. Existing `/api/health` compatibility is preserved.
- Sensitive project/API operations record actor, project, action, outcome, timestamp, and request ID without request bodies, credentials, generated source, or execution output. Responses include a validated or generated `X-Request-ID`.
- SQLite online backup/restore is available through `python -m qa_mcp.operations backup` and `python -m qa_mcp.operations restore <backup-path>`. Backups are integrity-checked, atomically written with mode `0600` in a mode `0700` directory, and pruned to configured retention. Stop QA-MCP before restore and verify the restored service before resuming.
- The existing project-centric UI is unchanged in structure. It displays the signed-in identity and minimal sign-in, session-expiry, and access-denied states.

### Configuration

Production must set `QA_ENVIRONMENT=production` and `QA_AUTH_MODE=google`, then configure the Google OAuth client ID/secret, exact callback URI, Google Workspace domain, session secret, and global-admin Google subject IDs. Explicit legacy project mappings are required before mapped members can access old projects. See Sections 16 and 17 for the environment-variable contract. Never commit the values or a populated `.env` file.

### Validation

```text
Focused security, workflow, execution, and MCP tests: 39 passed, 2 warnings
Full regression:                                  348 passed, 8 warnings, 0 failures
Browser verification:                             passed (mocked OIDC identity/access states and existing P2-S9.16 workflows)
JavaScript syntax checks:                         passed
MCP launched stdio tool inventory:                 passed (all 35 registered tools)
SQLite online backup/restore/integrity/retention:  passed
git diff --check:                                  clean
```

Google OIDC callback behavior was verified through a mocked identity boundary; no live Google credentials or organization deployment were used. P2-S9.17 does not claim deployment readiness until the organization's Google client/domain settings, HTTPS callback, production secret provisioning, legacy ownership mappings, and operational backup schedule are configured and verified. SQLite remains a single-host store, and automation remains a local subprocess rather than a sandbox. Model C network exposure and Model D untrusted execution remain out of scope.

### Model B Readiness Assessment

A post-P2-S9.17 production-readiness audit was completed on 2026-10-09. The audit covered 12 security and operational areas including continuity, authentication, authorization, web security, MCP boundary, execution security, database/recovery, legacy data, health/operations, UI/workflow, test confidence, and Model B deployment readiness.

**Readiness Classification:** READY FOR MODEL B WITH DEPLOYMENT/OPERATIONAL PREREQUISITES

The technical implementation is complete for a trusted internal QA-team platform (Model B). Deployment requires configuration of Google OAuth credentials, Workspace domain, production session secret, global administrator subjects, legacy project ownership mappings, HTTPS deployment, and operational backup scheduling. Model C network exposure hardening and Model D untrusted execution sandboxing remain explicitly out of scope.

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

Execution IDs are UUID-based identifiers generated by the execution service.

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
# Google OIDC production configuration (required when QA_AUTH_MODE=google)
GOOGLE_OIDC_CLIENT_ID=
GOOGLE_OIDC_CLIENT_SECRET=
GOOGLE_OIDC_REDIRECT_URI=https://qa.example.test/auth/callback
GOOGLE_WORKSPACE_DOMAIN=your-workspace-domain.example
QA_SESSION_SECRET=
# Optional identity/project administration settings
QA_GLOBAL_ADMIN_SUBJECTS=
QA_LEGACY_PROJECT_OWNERS={}
```

The Google entries above are placeholders. Do not use a domain or credentials
that have not been supplied for the deployment.

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
| `GOOGLE_OIDC_CLIENT_ID` | Google OAuth web client ID | No |
| `GOOGLE_OIDC_CLIENT_SECRET` | Google OAuth web client secret | **YES** |
| `GOOGLE_OIDC_REDIRECT_URI` | Exact registered OIDC callback URI | No |
| `GOOGLE_WORKSPACE_DOMAIN` | Allowed Google Workspace hosted domain | No |
| `QA_SESSION_SECRET` | Signs QA-MCP browser sessions; use at least 32 random characters | **YES** |
| `QA_GLOBAL_ADMIN_SUBJECTS` | Comma-separated stable Google `sub` identifiers for global administrators | No |
| `QA_LEGACY_PROJECT_OWNERS` | JSON mapping of legacy project IDs to Google `sub` identifiers | No |

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

# 17. CONFIGURATION AND ENVIRONMENT CONTRACT

The primary application configuration file is:

`config/settings.yaml`

The application also supports environment-specific configuration through environment variables.

Environment variables take precedence over default configuration values where supported by the implementation.

## Application configuration

The configuration file contains settings for:

- Application metadata
- LLM provider and model configuration
- Feature flags
- Automation execution
- Identity, authentication, and project authorization
- SQLite database and backup/recovery
- Jira
- GitHub
- Slack

## Automation environment variables

| Variable | Purpose |
|---|---|
| `DEFAULT_TEST_ENV` | Default execution environment when no environment is explicitly selected |
| `QA_BASE_URL` | Base URL for the QA environment |
| `STAGE_BASE_URL` | Base URL for the staging environment |
| `PROD_BASE_URL` | Base URL for the production environment |
| `QA_AUTOMATION_TIMEOUT_SECONDS` | Automation execution timeout in seconds |
| `QA_AUTOMATION_WORKSPACE_ROOT` | Root directory used for automation execution workspaces |
| `QA_AUTOMATION_KEEP_WORKSPACE` | Controls whether automation workspaces are retained after execution |
| `QA_AUTH_MODE` | `google` for Google OIDC; explicit `development` mode is only valid outside production |
| `QA_ENVIRONMENT` | Application environment; production requires Google OIDC configuration |
| `QA_SESSION_MAX_AGE_SECONDS` | Maximum signed browser session age |
| `QA_SESSION_COOKIE_SECURE` | Enables Secure session cookies; required in production |
| `QA_DATABASE_PATH` | SQLite database file path |
| `QA_BACKUP_DIRECTORY` | Protected SQLite backup destination directory |
| `QA_BACKUP_RETENTION` | Number of verified backups to retain |

## Integration environment variables

| Variable | Purpose | Secret? |
|---|---|---|
| `JIRA_URL` | Jira Cloud base URL | No |
| `JIRA_EMAIL` | Jira API account email | No, but treat as configuration |
| `JIRA_API_TOKEN` | Jira API authentication | Yes |
| `GITHUB_URL` | GitHub API base URL | No |
| `GITHUB_TOKEN` | GitHub API authentication | Yes |
| `GITHUB_OWNER` | GitHub username or organization | No |
| `SLACK_URL` | Slack API base URL | No |
| `SLACK_TOKEN` | Slack API authentication | Yes |
| `SLACK_DEFAULT_CHANNEL` | Default Slack channel | No |

## Model B authentication and database operations

For production, set `QA_ENVIRONMENT=production`, `QA_AUTH_MODE=google`,
`QA_SESSION_COOKIE_SECURE=true`, all five Google/session settings shown above,
and an HTTPS callback URL registered in the Google OAuth client. Configure the
Workspace domain rather than hard-coding it in application code. Set
`QA_LEGACY_PROJECT_OWNERS` explicitly for every existing project that should
be available to a project member; keys are project IDs and values are Google
stable subject IDs (`sub`). An unmapped project remains inaccessible to
members and causes readiness to report `mapping_required`.

Project membership uses `global_admin` and `project_member`. Configure at least
one trusted global administrator with `QA_GLOBAL_ADMIN_SUBJECTS`; administrators
can provision additional project members through the protected membership API.
The development actor is a fixed server-side identity, cannot be selected by
request headers or query values, and cannot start in production.

Create a consistent active-database backup with:

```bash
python -m qa_mcp.operations backup
```

The operation uses SQLite's online backup API, verifies `PRAGMA integrity_check`,
sets backup directory/file permissions to `0700`/`0600`, and retains the newest
`QA_BACKUP_RETENTION` files. To restore, stop QA-MCP, run:

```bash
python -m qa_mcp.operations restore /protected/path/to/qa_mcp-backup.sqlite3
```

The restore path verifies both the source backup and restored database. Restart
QA-MCP only after the restore succeeds and readiness is healthy. Keep backup
storage on protected single-host local storage, schedule backups through the
deployment's existing operations tooling, and periodically perform a restore
drill. Do not use a shared network filesystem as the live SQLite database.

## Example local configuration

The following values are examples only:

~~~yaml
application:
  name: qa-mcp
  environment: local

llm:
  provider: mock
  region: ""
  model_id: ""

features:
  requirement_analyzer: true
  testcase_generator: true
  testcase_reviewer: true
  jira_connector: false
  github_connector: false
  slack_connector: false
  automation_generator: false

automation_execution:
  base_url: ""
  timeout_seconds: 60
  workspace_root: ""
  keep_workspace: false

jira:
  url: ""
  email: ""
  api_token: ""

github:
  url: "https://api.github.com"
  token: ""
  owner: ""

slack:
  url: "https://slack.com/api"
  token: ""
  default_channel: ""
~~~

## Example `.env` template

These are placeholders only. Never commit real credentials or secrets.

~~~dotenv
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email
JIRA_API_TOKEN=your-token

GITHUB_URL=https://api.github.com
GITHUB_TOKEN=your-github-token
GITHUB_OWNER=your-github-username-or-org

SLACK_URL=https://slack.com/api
SLACK_TOKEN=
SLACK_DEFAULT_CHANNEL=

DEFAULT_TEST_ENV=qa
QA_BASE_URL=
STAGE_BASE_URL=
PROD_BASE_URL=
QA_AUTOMATION_TIMEOUT_SECONDS=60
QA_AUTOMATION_WORKSPACE_ROOT=
QA_AUTOMATION_KEEP_WORKSPACE=false
~~~

## Secret-handling rules

- Never commit real credentials, access tokens, API keys, passwords, or production secrets.
- Use environment variables or a local ignored `.env` file for secrets.
- Never paste populated secret values into this README.
- Verify that `.env` is protected by `.gitignore`.
- Review `git diff` before committing configuration changes.
- Run `git diff --check`.
- Run focused tests.
- Run the full regression suite.
- Update this README with verified results before committing.

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

# 21. HISTORICAL EXECUTION-HARDENING ROADMAP

This section is retained for historical continuity.

It is not the current development checkpoint.

The current development checkpoint is defined at the beginning of this README.
This historical roadmap has been superseded by the completed P2-S9.12 and
P2-S9.14 checkpoints and the current P2-S9.15 implementation.

The earlier P2-S9.1 execution-hardening roadmap has been superseded by the completed implementation and later P2-S9.12 work.

Historical direction included:

- Safe workspace and file handling
- Stronger command validation
- Execution identity
- Configurable limits
- Failure classification
- Artifact and result retention
- Execution evidence
- Execution history
- Reporting and analysis
- Failure analysis
- Web dashboard integration
- Agent orchestration

The completed historical checkpoints below must be preserved as historical records only.

Future work must follow the current checkpoint at the top of this README and must not return to already-completed functionality without a new, explicitly documented requirement.

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

**P2-S9.17 — Internal Identity, Project Authorization, and Execution Credential Isolation**

P2-S9.14-A — QA-MCP Production UI Architecture Shell, P2-S9.14-B — Project
Execution Insights, and P2-S9.14-C — Generated Automation Artifact Review are
complete and must not be recreated. P2-S9.14-D — Persisted Test Case Review
is complete, committed as `207e31e`, and pushed to `origin/main`. P2-S9.15
corrects persisted automation artifact identity while preserving legacy
records and existing execution behavior. P2-S9.15 is complete, committed as
`ba9e27c`, and pushed to `origin/main`.

Previous completed checkpoints:

```text
P2-S8.6   Automation Candidate Selection          COMPLETE
P2-S8.7   Candidate → Automation Generation       COMPLETE
P2-S8.8   Automation Case Validation              COMPLETE
P2-S8.8+  Automation Code Generation              COMPLETE
P2-S8.9   Controlled Automation Execution         COMPLETE
```

P2-S9.14-B verified baseline:

```text
Focused web tests: 30 passed
Full regression: 327 passed
8 warnings
0 failures
```

P2-S9.14-B checkpoint commit: `7439119`.
P2-S9.14-C checkpoint commit: `f5dbc8d` — Complete P2-S9.14-C generated
artifact review. P2-S9.14-D checkpoint commit: `207e31e` — Complete
P2-S9.14-D persisted test case review. It was pushed to `origin/main` with a
clean working tree. Its validation baseline was 327 passed, 8 warnings, and
0 failures.

P2-S9.15 validation baseline: 329 passed, 8 warnings, and 0 failures.
P2-S9.16 — Project-Centric QA Workspace UX is complete, committed as
`6b8c532`, and pushed to `origin/main`. P2-S9.17 — Internal Identity, Project
Authorization, and Execution Credential Isolation is complete, committed as
`5759211` (implementation) and `f94f05c` (corrective commit for local development
operator access), and pushed to `origin/main`. P2-S9.17 validation baseline:
349 passed (full regression), 8 warnings, and 0 failures. Model B remains the
approved product direction; Model C and Model D remain out of scope.

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
5. Treat **P2-S9.17 — Internal Identity, Project Authorization, and Execution Credential Isolation** as the latest implementation checkpoint. P2-S9.17 is committed as `5759211` (implementation) and `f94f05c` (corrective commit for local development operator access) and pushed to `origin/main`. P2-S9.16 remains committed as `6b8c532`; P2-S9.15 remains committed as `ba9e27c`. Model B is the approved deployment direction; Model C and Model D remain out of scope.
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


---

## P2-S9.2 — Executable Playwright Code Generation

Status: COMPLETE

Implementation commit:

```text
176ab59 Implement executable Playwright code generation
```

Implemented in:

```text
src/qa_mcp/core/automation/code_generation_service.py
```

Generated Playwright/Python artifacts now translate the controlled automation DSL into executable Playwright code.

Supported automation steps:

```text
goto: <url>
fill: <selector> = <value>
click: <selector>
press: <selector> = <key>
```

Supported assertions:

```text
visible: <selector>
text: <selector> = <expected text>
url: <expected url>
```

The generator now:

- Produces executable Playwright/Python code instead of comments.
- Generates `Page` and `expect` based Playwright code.
- Rejects unsupported automation steps.
- Rejects unsupported automation assertions.
- Validates malformed step/assertion expressions.
- Preserves the existing `GeneratedAutomationArtifact` contract.
- Keeps the existing `execute_automation_code` MCP boundary unchanged.
- Supports generated-artifact → execution-service integration.

Verification:

```text
pytest -q tests/test_automation_code_generation_service.py tests/test_automation_code_generation_empty.py tests/test_automation_code_generation_result.py

8 passed
0 failures

pytest -q tests/test_automation_execution_service.py

17 passed
0 failures

pytest -q

216 passed
7 warnings
0 failures

git diff --check
clean
```

The 7 pytest/Pydantic warnings are existing non-blocking technical debt and are not part of P2-S9.2.

### Current implementation state

```text
Requirement/Test Case
        ↓
Automation Candidate
        ↓
Automation Case
        ↓
Generated Playwright/Python Artifact
        ↓
Controlled Automation Execution
        ↓
Execution Result
```

### Next implementation checkpoint

```text
P2-S9.3 — Real Playwright Execution Validation
```

Do not redesign or rebuild completed automation generation, validation, artifact generation, workspace handling, command boundary, execution configuration, or controlled execution functionality.

---

---

## P2-S9.3 — Execution History and Persistence

Status: COMPLETE

Implementation commit:

```text
7b8a67b Add automation execution history
```

Verification:

```text
Focused execution/history suite: 26 passed
Full regression suite: 227 passed
Warnings: 7 existing non-blocking warnings
Failures: 0
git diff --check: clean
```

### Implementation delivered

- Unique execution IDs are generated for every automation execution.
- Automation execution results are persisted in SQLite.
- Execution history can be retrieved by execution ID.
- Execution history can be listed with optional automation-case filtering and result limits.
- `execute_automation_code` now persists execution results.
- Added MCP tool: `get_automation_execution`.
- Added MCP tool: `list_automation_executions`.
- Added repository, application-service, execution-service, and MCP-tool test coverage.
- Existing execution behavior and contracts remain intact.

### Current implementation state

```text
Requirement/Test Case
        ↓
Automation Candidate
        ↓
Automation Case
        ↓
Generated Playwright/Python Artifact
        ↓
Controlled Automation Execution
        ↓
Execution Result
        ↓
Persistent Execution History
        ↓
Reporting / Analysis
```

### Next implementation checkpoint

```text
P2-S9.4 — Reporting / Analysis
```

Do not redesign or rebuild completed automation generation, validation, artifact generation, workspace handling, command boundary, execution configuration, controlled execution, or execution-history functionality.

---

## P2-S9.4 — Reporting / Analysis

Status: COMPLETE

Implementation commit: 55ddd09 Add automation execution reporting

Verification:

```text
Focused P2-S9.4 tests: 12 passed
Full regression suite: 234 passed
Warnings: 7 existing non-blocking warnings
Failures: 0
git diff --check: clean
```

### Implementation delivered

- Added aggregated automation execution reporting.
- Added execution totals by result status.
- Added pass-rate calculation.
- Added total and average execution duration metrics.
- Added latest execution identification and status.
- Added optional automation-case filtering.
- Added persistent SQLite-backed reporting.
- Added reporting application-service support.
- Added MCP reporting capability.
- Added repository, service, and MCP-tool test coverage.

### Current implementation state

```text
Requirement/Test Case
        ↓
Automation Candidate
        ↓
Automation Case
        ↓
Generated Playwright/Python Artifact
        ↓
Controlled Automation Execution
        ↓
Execution Result
        ↓
Persistent Execution History
        ↓
Execution Reporting / Analysis
```

### Next implementation checkpoint

```text
P2-S9.5 — Next functional capability
```

Do not redesign or rebuild completed automation generation, validation, artifact generation, workspace handling, command boundary, execution configuration, controlled execution, execution history, or reporting functionality.

---

## P2-S9.5 — Failure Analysis

Status: COMPLETE

Implementation commit: 77a8d9b Add automation execution failure analysis

Verification:

```text
Focused P2-S9.5 tests: 15 passed
Full regression suite: 242 passed
Warnings: 7 existing non-blocking warnings
Failures: 0
git diff --check: clean
```

### Implementation delivered

- Added structured automation execution failure analysis.
- Added failure-analysis models and application-service support.
- Added persisted failure-analysis retrieval from execution history.
- Added analysis of failed and errored executions.
- Added execution identifiers, automation artifact identifiers, and automation case traceability.
- Added MCP failure-analysis capability.
- Added repository, service, and MCP-tool test coverage.

### Current implementation state

```text
Requirement/Test Case
        ↓
Automation Candidate
        ↓
Automation Case
        ↓
Generated Playwright/Python Artifact
        ↓
Controlled Automation Execution
        ↓
Execution Result
        ↓
Persistent Execution History
        ↓
Execution Reporting / Analysis
        ↓
Failure Analysis
```

### Next implementation checkpoint

```text
P2-S9.6 — Next functional capability
```

Do not redesign or rebuild completed automation generation, validation, artifact generation, workspace handling, command boundary, execution configuration, controlled execution, execution history, reporting, or failure-analysis functionality.

---

## P2-S9.6 — Web Dashboard

Status: COMPLETE

Implementation commit: 79e3c3f Add web dashboard

Verification:

```text
Focused Web Dashboard tests: 5 passed
Full regression suite: 247 passed
Warnings: 8 existing non-blocking warnings
Failures: 0
git diff --check: clean
```

### Implementation delivered

- Added FastAPI-based web application.
- Added browser-accessible QA automation dashboard.
- Added execution reporting view.
- Added execution history view.
- Added failure-analysis view.
- Added REST endpoints for execution reporting, execution history, and failure analysis.
- Added dedicated web entrypoint through `run_web.py`.
- Added web dashboard automated test coverage.
- Added FastAPI to `requirements.txt`.

### Start the Web Dashboard

From the project root with the virtual environment activated:

```bash
cd ~/pythonPrograms/qa-mcp
source .venv/bin/activate
python run_web.py
```

The dashboard is then available at:

```text
http://127.0.0.1:8000
```

### Web API endpoints

```text
GET /
GET /api/executions/report
GET /api/executions?limit=20
GET /api/executions/failures?limit=20
```

### Current implementation state

```text
Requirement/Test Case
        ↓
Automation Candidate
        ↓
Automation Case
        ↓
Generated Playwright/Python Artifact
        ↓
Controlled Automation Execution
        ↓
Execution Result
        ↓
Persistent Execution History
        ↓
Execution Reporting / Analysis
        ↓
Failure Analysis
        ↓
Web Dashboard
```

### Next implementation checkpoint

```text
P2-S9.7 — Next functional capability
```

Do not redesign or rebuild completed automation generation, validation, artifact generation, workspace handling, command boundary, execution configuration, controlled execution, execution history, reporting, failure analysis, or web-dashboard functionality.

---

## P2-S9.7 — AI QA Workspace

Status: COMPLETE

Implementation scope:

- Added a browser-based AI QA Workspace to the existing web dashboard.
- Added persistent QA project creation and retrieval.
- Added project-aware requirement analysis.
- Added project-aware QA test-suite generation.
- Added AI-generated test-case review.
- Added requirement version persistence.
- Added QA-suite version persistence.
- Added workspace REST APIs.
- Added deterministic MockLLM support for workspace development and tests.
- Added automated coverage for project, workspace service, and MockLLM behavior.
- Preserved all existing execution, reporting, failure-analysis, and dashboard functionality.

### AI QA Workspace flow

```text
QA Project
    ↓
Requirement
    ↓
Requirement Analysis
    ↓
Test Case Generation
    ↓
AI Test Case Review
    ↓
Requirement Version
    ↓
QA Suite Version
    ↓
Persisted QA Workspace Result
```

### Workspace API endpoints

```text
POST /api/projects
GET  /api/projects/{project_id}
POST /api/projects/{project_id}/qa-suite
```

### Workspace behavior

A QA project must exist before a QA suite can be generated for that project.

Existing projects can be retrieved using:

```text
GET /api/projects/{project_id}
```

A requirement can then be submitted using:

```text
POST /api/projects/{project_id}/qa-suite
```

The generated response contains:

```text
project
requirement_version
suite_version
requirement
analysis
test_cases
review
```

Requirement versions and QA-suite versions are persisted independently so that generated QA work remains traceable to the project and requirement history.

### Verification

```text
Focused S9.7 workspace tests: 19 passed
Full regression suite: 261 passed
Warnings: 8 existing non-blocking warnings
Failures: 0
git diff --check: clean
```

### Current implementation state

```text
Requirement/Test Case
        ↓
Automation Candidate
        ↓
Automation Case
        ↓
Generated Playwright/Python Artifact
        ↓
Controlled Automation Execution
        ↓
Execution Result
        ↓
Persistent Execution History
        ↓
Execution Reporting / Analysis
        ↓
Failure Analysis
        ↓
Web Dashboard
        ↓
AI QA Workspace
        ↓
Project-aware Requirement Analysis
        ↓
Versioned QA Suite
```

### P2-S9.8 — Automation Candidate Selection

Status: COMPLETE

Implementation scope:

- Connected the AI QA Workspace to the existing Automation Candidate Service.
- Added automation candidate selection to QA-suite generation.
- Added automation candidate results to the generated QA-suite response.
- Preserved manual-test identification through the existing candidate-selection workflow.
- Added focused regression coverage for automation candidate selection.
- Preserved all existing QA Workspace, execution, reporting, failure-analysis, and dashboard functionality.

### Automation Candidate flow

```text
QA Project
    ↓
Requirement
    ↓
Requirement Analysis
    ↓
Test Case Generation
    ↓
AI Test Case Review
    ↓
Automation Candidate Selection
    ↓
Requirement Version
    ↓
QA Suite Version
    ↓
Persisted QA Workspace Result
```

### QA-suite response

The generated QA-suite response now includes:

```text
automation_candidates
    candidate_ids
    manual_ids
    total
```

Candidate selection is performed through the existing:

```text
AutomationCandidateService
        ↓
AutomationCandidateSelector
```

### Verification

```text
Focused S9.8 workspace-service tests: 2 passed
Full regression suite: 261 passed
Warnings: 8 existing non-blocking warnings
Failures: 0
git diff --check: clean
```

### Current implementation state

```text
Requirement/Test Case
        ↓
Automation Candidate
        ↓
Automation Case
        ↓
Generated Playwright/Python Artifact
        ↓
Controlled Automation Execution
        ↓
Execution Result
        ↓
Persistent Execution History
        ↓
Execution Reporting / Analysis
        ↓
Failure Analysis
        ↓
Web Dashboard
        ↓
AI QA Workspace
        ↓
Project-aware Requirement Analysis
        ↓
Versioned QA Suite
        ↓
Automation Candidate Selection
```

### P2-S9.9 — AI QA Workspace Automation Generation

Status: COMPLETE

Implementation scope:

- Connected the AI QA Workspace to the existing automation candidate generation service.
- Added dependency injection for automation candidate generation.
- Added automation case generation during QA-suite creation.
- Added generated automation cases to the QA-suite response.
- Preserved the existing automation candidate selection flow.
- Added focused regression coverage for automation generation.
- Preserved all existing QA Workspace, candidate selection, execution, reporting, failure-analysis, and dashboard functionality.

### AI QA Workspace automation flow

```text
QA Project
    ↓
Requirement
    ↓
Requirement Analysis
    ↓
Test Case Generation
    ↓
AI Test Case Review
    ↓
Automation Candidate Selection
    ↓
Automation Case Generation
    ↓
Requirement Version
    ↓
QA Suite Version
    ↓
Persisted QA Workspace Result
```

### QA-suite automation response

The generated QA-suite response now includes:

```text
automation_candidates
    candidate_ids
    manual_ids
    total

automation_cases
    test_case_id
    automation_type
```

Automation generation is performed through the existing service boundary:

```text
AutomationCandidateGenerationService
        ↓
Generated Automation Cases
```

### Verification

```text
Focused S9.9 workspace-service tests: 2 passed
Full regression suite: 261 passed
Warnings: 8 existing non-blocking warnings
Failures: 0
git diff --check: clean
```

### Current implementation state

```text
Requirement/Test Case
        ↓
Automation Candidate
        ↓
Automation Case
        ↓
Generated Playwright/Python Artifact
        ↓
Controlled Automation Execution
        ↓
Execution Result
        ↓
Persistent Execution History
        ↓
Execution Reporting / Analysis
        ↓
Failure Analysis
        ↓
Web Dashboard
        ↓
AI QA Workspace
        ↓
Project-aware Requirement Analysis
        ↓
Versioned QA Suite
        ↓
Automation Candidate Selection
        ↓
Automation Case Generation
```

### P2-S9.10 — AI QA Workspace Automation Wiring

Status: COMPLETE

Implementation scope:

- Connected the production web application to the existing automation-generation pipeline.
- Added the workspace automation case generator using the workspace LLM.
- Added the workspace automation service.
- Added the existing automation candidate service and selector to the production workspace.
- Added the automation candidate generation service to the AI QA Workspace.
- Connected `QAWorkspaceService` to the production automation candidate generation service.
- Added focused regression coverage confirming the production dependency is injected correctly.
- Preserved all existing QA Workspace, candidate selection, automation generation, execution, reporting, failure-analysis, and dashboard functionality.

### Automation generation flow

```text
QA Project
    ↓
Requirement
    ↓
Requirement Analysis
    ↓
Test Case Generation
    ↓
AI Test Case Review
    ↓
Automation Candidate Selection
    ↓
Automation Candidate Generation
    ↓
Automation Case Generation
    ↓
Requirement Version
    ↓
QA Suite Version
    ↓
Persisted QA Workspace Result
```

### Production wiring

```text
Workspace LLM
      ↓
AutomationCaseGenerator
      ↓
AutomationService
      ↓
AutomationCandidateGenerationService
      ↑
AutomationCandidateService
      ↑
AutomationCandidateSelector
      ↓
QAWorkspaceService
      ↓
AI QA Workspace API
```

The web application now constructs the real automation-generation dependencies instead of relying on test-only or implicit service construction.

### Verification

```text
Focused S9.10 workspace-service tests: 3 passed
Full regression suite: 262 passed
Warnings: 8 existing non-blocking warnings
Failures: 0
git diff --check: clean
```

### Current implementation state

```text
Requirement/Test Case
        ↓
Automation Candidate
        ↓
Automation Case
        ↓
Generated Playwright/Python Artifact
        ↓
Controlled Automation Execution
        ↓
Execution Result
        ↓
Persistent Execution History
        ↓
Execution Reporting / Analysis
        ↓
Failure Analysis
        ↓
Web Dashboard
        ↓
AI QA Workspace
        ↓
Project-aware Requirement Analysis
        ↓
Versioned QA Suite
        ↓
Automation Candidate Selection
        ↓
Automation Candidate Generation
        ↓
Automation Case Generation
```

#
## P2-S9.12 — Project Workspace Execution History and Result Review

Implemented:
- Added project-scoped execution history listing.
- Added project-scoped execution lookup.
- Added project-scoped execution reporting.
- Added project-scoped failure analysis.
- Added artifact ownership filtering through the project artifact repository.
- Added API coverage for project execution history and result review.

Verification:
- Focused tests: 4 passed.
- Full regression: 310 passed, 8 warnings.
- git diff --check: passed.

Next implementation:
- Audit remaining backend-to-UI integration.
- Define and implement the QA Agent `skills.md` capability.

## P2-S9.12 — Test Case Persistence and Automation Candidate Workflow

Status: IN PROGRESS

Current implementation state:

- Persistent Project QA Workspace is implemented.
- Persisted project requirements, requirement versions, saved QA suite versions, test cases, automation candidates, and generated automation artifacts are exposed through the workspace.
- Automation candidates are now actionable from the Project QA Workspace.
- Added `QAProjectAutomationGenerationRequest` for project-level automation generation requests.
- Added `QAWorkspaceService.generate_automation_from_project()` to continue from persisted test cases.
- Persisted test-case dictionaries are reconstructed through the existing `TestCase` model before candidate processing.
- Requested test-case IDs are validated against the persisted project workspace.
- Selected test cases are rechecked through the existing `AutomationCandidateService`.
- Non-candidate selections are rejected instead of bypassing the existing candidate policy.
- Existing `AutomationCandidateGenerationService` is reused to generate automation cases.
- Existing `AutomationCodeGenerationService` is reused to generate automation artifacts.
- Added `POST /api/projects/{project_id}/automation`.
- Added Project QA Workspace UI controls for selecting automation candidates.
- Added a Generate Automation action in the Project QA Workspace.
- Browser-side UI wiring invokes the new project automation endpoint and refreshes the persisted workspace state.
- Existing Generate QA Suite functionality remains separate and unchanged.
- Added dashboard/API regression coverage for the new workflow.
- Focused workspace/dashboard tests: 34 passed.
- Full regression suite: 302 passed, 8 known non-blocking warnings, 0 failures.
- `git diff --check` is clean.

P2-S9.12 product flow:

Project
  -> Requirement
  -> Requirement Analysis
  -> Test Case Generation
  -> AI Review
  -> Preview
  -> User selects test cases
  -> Save
  -> QASuiteVersioningService
  -> SQLite qa_suite_versions
  -> Project QA Workspace
       -> Existing Requirements
       -> Requirement Versions
       -> Saved Suite Versions
       -> Existing Test Cases
       -> Automation Candidates
       -> Select Automation Candidates
       -> Generate Automation
       -> Automation Case Generation
       -> Automation Artifact Generation
       -> Controlled Automation Execution
       -> Execution History / Reporting
       -> Failure Analysis

Implemented user capability:

- View requirements already provided or prepared for the project.
- View requirement analysis and version information already prepared.
- View test cases already generated and persisted for the project.
- View automation candidates derived from persisted test cases.
- Select one or more persisted automation candidates.
- Generate automation from the selected candidates.
- Generate automation artifacts through the existing automation code-generation pipeline.
- Keep generated automation associated with the project workspace.
- Preserve the existing active Generate QA Suite workflow independently.

Remaining P2-S9.12 scope:

Project QA Workspace
  -> View persisted test cases
  -> View automation candidates
  -> Select automation candidates
  -> Generate/use automation cases
  -> Validate automation cases
  -> Generate automation artifacts
  -> Controlled automation execution
  -> Execution result/history/reporting
  -> Failure analysis

Completed automation candidate selection, candidate generation, automation case generation, validation, Playwright code generation, artifact generation, command-boundary enforcement, execution configuration, controlled execution, execution history, reporting, and failure-analysis services must continue to be reused rather than rebuilt.

Checkpoint status at P2-S9.12:

P2-S9.12 — Controlled Automation Execution from Project QA Workspace

The Project QA Workspace now supports controlled execution of persisted automation artifacts. Execution is scoped to the selected project, reuses the existing controlled execution pipeline, and persists results through the existing execution-history service.

Implemented in this continuation:

- Added project-scoped persisted automation-artifact lookup.
- Added controlled execution through the existing `AutomationExecutionService`.
- Added execution-result persistence through `AutomationExecutionHistoryService`.
- Added `POST /api/projects/{project_id}/automation/{artifact_id}/execute`.
- Added Execute actions for generated automation artifacts in the Project QA Workspace.
- Added workspace feedback for execution status, stdout, stderr, and errors.
- Preserved existing automation generation, validation, artifact generation, command-boundary enforcement, execution configuration, reporting, and failure-analysis functionality.

Validation completed:

```text
Python compilation:                 passed
Full regression suite:              306 passed
Warnings:                            8 known non-blocking warnings
Failures:                            0
git diff --check:                    clean
```

The Project QA Workspace QA-suite generation flow has been hardened to require a complete test-case suite covering the supplied positive scenarios, negative scenarios, and edge cases. The generator now rejects malformed or incomplete LLM payloads instead of silently normalizing them into a single test case.

The LLM generation boundary now distinguishes unusable provider output from application validation failures. In particular, a provider/guardrail refusal is surfaced as `LLMGenerationError` and returned by the QA-suite API as HTTP 502 rather than being incorrectly classified as HTTP 404.

During validation, the configured Bedrock provider returned the following non-JSON response:

`The response was blocked by dev-guardrails policy. If this looks like a false positive, ping #ai-guardrails.`

This confirmed that the observed single-test-case UI symptom was not caused by application-side test-case truncation. The provider response was blocked before a test-case suite could be produced.

Validation completed:

```text
Focused generator/dashboard tests:  30 passed
Full regression suite:              304 passed
Warnings:                            8 known non-blocking warnings
Failures:                            0
git diff --check:                    clean
```
The provider-failure diagnostic path now preserves the raw LLM provider response on `LLMGenerationError.provider_response` and logs that response at error level for IT troubleshooting. The API continues to return only the safe generic HTTP 502 message and does not expose the provider response to the end user.

The diagnostic regression test verifies that the exact provider response is retained. Focused diagnostic validation passed with 39 tests, and the full regression suite remains at 304 passed with 8 known non-blocking warnings and 0 failures.

The implementation is intentionally limited to prompt hardening, strict test-case response validation, LLM-generation error classification, API error mapping, and regression coverage. Do not bypass or weaken provider/dev-guardrail policy as part of this fix.

Next implementation:

P2-S9.12 continuation — Project Workspace Execution History and Result Review

The next implementation should expose persisted execution history and result review from the Project QA Workspace by reusing the existing execution-history, reporting, and failure-analysis services.

Do not redesign or rebuild completed automation generation, validation, artifact generation, workspace handling, command boundary, execution configuration, controlled execution, execution history, reporting, failure analysis, web-dashboard functionality, AI QA Workspace functionality, automation candidate selection functionality, automation case generation functionality, production automation-generation wiring, automation artifact generation, or the QA-suite generation/error-boundary hardening completed in this checkpoint.

### P2-S9.11 — AI QA Workspace Artifact Generation

Status: COMPLETE

Implementation scope:

- Connected the AI QA Workspace to the existing automation code-generation service.
- Added production construction of `AutomationCodeGenerationService`.
- Connected the service to `QAWorkspaceService` through dependency injection.
- Added automation artifact generation for generated automation cases.
- Added `automation_artifacts` to the QA-suite workspace response.
- Added persistent SQLite repository support for QA Workspace automation artifacts.
- Added focused regression coverage for artifact persistence, artifact generation, and dependency injection.
- Added browser-level Playwright regression coverage for the AI QA Workspace dashboard.
- Verified the rendered dashboard preserves the AI QA Workspace and existing Automation Execution Overview.
- Preserved all existing QA Workspace, candidate selection, automation generation, execution, reporting, failure-analysis, and dashboard functionality.

### Automation artifact flow

```text
QA Project
    ↓
Requirement
    ↓
Requirement Analysis
    ↓
Test Case Generation
    ↓
AI Test Case Review
    ↓
Automation Candidate Selection
    ↓
Automation Candidate Generation
    ↓
Automation Case Generation
    ↓
Automation Code Generation
    ↓
Automation Artifact
    ↓
Persistent Artifact Repository
    ↓
QA Workspace Response
```

### Workspace response

The generated QA-suite response now includes:

```text
automation_candidates
automation_cases
automation_artifacts
requirement_version
suite_version
```

### Production wiring

```text
Workspace LLM
      ↓
AutomationCaseGenerator
      ↓
AutomationService
      ↓
AutomationCandidateGenerationService
      ↓
AutomationCase
      ↓
AutomationCodeGenerationService
      ↓
AutomationArtifact
      ↓
QAWorkspaceService
      ↓
AI QA Workspace API
```

### Dashboard regression protection

The AI QA Workspace is protected by both structural and browser-level regression tests.

The dashboard regression coverage verifies:

```text
AI QA Workspace
      ↓
Create QA Project controls
      ↓
Generate QA Suite controls
      ↓
Project / requirement inputs
      ↓
JavaScript action wiring
      ↓
Workspace API wiring
      ↓
Rendered dashboard
      ↓
Existing Automation Execution Overview preserved
```

The browser regression test uses Playwright with Chromium against a live Uvicorn instance and verifies the rendered dashboard and the important workspace controls.

The browser regression test is now part of the permanent dashboard regression suite and must remain green during future UI changes.

### Verification

```text
Focused dashboard/workspace tests: 12 passed
Browser regression test:           1 passed, 11 deselected
Full regression suite:             269 passed
Warnings:                           8 known non-blocking warnings
Failures:                           0
git diff --check:                   clean
```

**P2-S9.11 is complete. Do not recreate or redesign this capability.**

### Next implementation checkpoint

```text
P2-S9.12 — Test Case Persistence and Automation Candidate Workflow
```

P2-S9.12 has progressed from the persistent Project QA Workspace to actionable automation-candidate selection and generation. The workspace can now select persisted automation candidates and invoke the existing automation generation and artifact-generation pipeline. This implementation is committed as `e186391`. The remaining work is to continue from generated automation artifacts into the completed controlled execution, execution-history, reporting, and failure-analysis pipeline.

Do not redesign or rebuild completed automation generation, validation, artifact generation, workspace handling, command boundary, execution configuration, controlled execution, execution history, reporting, failure analysis, web-dashboard functionality, AI QA Workspace functionality, automation candidate selection functionality, automation case generation functionality, production automation-generation wiring, or automation artifact generation.


---

## P2-S9.14-A — QA-MCP Production UI Architecture Shell

**Status: COMPLETE**

Implementation scope:

- Introduced explicit workflow navigation across the existing QA-MCP web UI.
- Added dedicated `/execution` workflow page.
- Added dedicated `/reports` workflow page.
- Added shared workflow navigation styling.
- Connected the Execution page to the existing execution reporting and execution-history APIs.
- Connected the Reports page to the existing execution reporting and failure-analysis APIs.
- Added dedicated JavaScript assets for the new workflow pages.
- Added regression coverage for the new page routes, navigation, and static assets.
- Preserved the existing Dashboard implementation.
- Preserved the existing Project QA Workspace implementation.
- Preserved all existing backend API contracts.
- No core business logic, persistence, execution, reporting, or failure-analysis services were redesigned.

### Production UI workflow structure

```text
QA MCP
  |
  +-- Dashboard
  |
  +-- Projects / QA Workspace
  |
  +-- Execution
  |      +-- Execution Metrics
  |      +-- Recent Executions
  |      +-- Execution History
  |
  +-- Reports & Analysis
         +-- Execution Reporting
         +-- Pass Rate
         +-- Average Duration
         +-- Failure Analysis
```

### Backend capability reuse

```text
Execution UI
    |
    +-- GET /api/executions/report
    +-- GET /api/executions?limit=20

Reports UI
    |
    +-- GET /api/executions/report
    +-- GET /api/executions/failures?limit=20
```

No duplicate execution or reporting business logic was introduced in the UI.

### Navigation

```text
Dashboard
Projects / QA Workspace
Execution
Reports & Analysis
```

The active workflow is visually identified on each page.

### Validation

```text
Focused web tests:                 29 passed
Full regression suite:             326 passed
Warnings:                            8 known non-blocking warnings
Failures:                            0
git diff --check:                    clean
Browser/API verification:            passed
```

**P2-S9.14-A is complete.**

Do not redesign or rebuild the existing Dashboard, Project QA Workspace, execution services, reporting services, failure-analysis services, or established backend API contracts as part of the next increment.

### Next implementation

**P2-S9.14-B — Production UI workflow expansion**

Before implementation:

1. Inspect the existing backend capabilities.
2. Identify stable APIs/services that already exist.
3. Define ONE next UI workflow boundary.
4. Do not invent backend capabilities merely to populate UI pages.
5. Do not redesign existing working workflows.
6. Obtain approval for the next sub-step before coding.


---

## P2-S9.14-B — Project Execution Insights

**Status: COMPLETE — committed as `7439119`**

### Implementation scope

- Added a compact Project Execution Insights section to the existing Project
  QA Workspace.
- Displays project-scoped total, passed, failed, error, and pass-rate metrics.
- Displays recent project-scoped failures with status, automation case,
  failure message, and a Review action.
- Reuses the existing project execution detail flow for failure review.
- Handles loading, no executions, no failures, unavailable failure details,
  and API errors explicitly.
- Refreshes project insights after the existing project automation execution
  action completes.
- Preserved existing workspace controls, Dashboard behavior, global Execution
  and Reports pages, backend services, and API contracts.

### Reused project-scoped capabilities

```text
GET /api/projects/{project_id}/executions/report
GET /api/projects/{project_id}/executions/failures?limit=10
GET /api/projects/{project_id}/executions/{execution_id}
```

No backend execution, reporting, failure-analysis, or persistence changes were
required.

### Validation

```text
Focused web tests:                 30 passed
Full regression suite:             327 passed
Warnings:                            8
Failures:                            0
git diff --check:                    clean
Browser verification:               passed
```

The browser verification covered project selection, project-scoped metrics and
failures, execution Review/detail, empty execution state, healthy no-failure
state, API error state, and continued availability of existing workspace
controls.

The P2-S9.14-B implementation is committed as `7439119` and was pushed to
`origin/main`. At the P2-S9.14-C baseline, `main` was synchronized with
`origin/main` and the working tree was clean.

### Follow-on checkpoint (completed)

**P2-S9.14-C — Generated Automation Artifact Review**

Adds read-only inspection of generated automation artifact source in the
existing Project QA Workspace, reusing artifact data already returned by the
workspace API. Review and Execute remain separate actions. No backend/API,
generation, persistence, or execution changes are in scope.


---


## P2-S9.14-C — Generated Automation Artifact Review

**Status: COMPLETE — committed as `f5dbc8d`**

### Implementation scope

- Added a Review action for each generated automation artifact in the existing
  Project QA Workspace.
- Added an inline read-only panel with filename, framework, language, creation
  time when available, project, associated test case, automation case, and
  generated source.
- Rendered generated source through DOM text nodes so markup-like source stays
  inert; the source area is scrollable for long files.
- Added close and artifact-switch behavior while leaving Execute as a separate
  action.
- Reused artifact data from the existing project workspace response. No new
  endpoint or backend/API contract was added.
- Preserved project scoping, artifact generation/persistence, execution
  semantics, Project Execution Insights, and other existing workflows.

### Validation

```text
Focused web tests:                 30 passed
Full regression suite:             327 passed
Warnings:                            8
Failures:                            0
JavaScript syntax check:             passed
git diff --check:                    clean
Browser verification:               passed
```

The browser verification covered artifact metadata and source display,
inert markup-like source, switching artifacts, closing review, no execution
request from Review, and the existing project-scoped Execute action working
independently. The P2-S9.14-B execution insights flow remained covered by the
same browser regression.

The P2-S9.14-C implementation is committed as `f5dbc8d` and is present on
`origin/main`.


---


## P2-S9.14-D — Persisted Test Case Review

**Status: COMPLETE — committed as `207e31e`**

### Implementation scope

- Added a Review action to each persisted test case row in the existing
  Project QA Workspace.
- Displays preconditions, ordered steps, expected result, priority, test type,
  and the exact suite ID/version and requirement-version metadata supplied by
  that workspace row.
- Binds review to the selected row, so identical test case IDs in separate
  suite versions retain their row-specific metadata.
- Uses DOM text APIs for testcase values; markup-like content remains inert.
- Keeps Review separate from candidate selection, artifact review, and
  execution. No backend/API, persistence/schema, integration, or execution
  changes were made.

### Validation

```text
Focused web tests:                 30 passed
Full regression suite:             327 passed
Warnings:                            8
Failures:                            0
JavaScript syntax check:             passed
git diff --check:                    clean
Browser verification:               passed
```

Browser coverage verified case-specific details and version metadata,
precondition and step ordering, inert markup-like values, switching and
closing review, no mutation/generation/execution requests, candidate
selection, artifact review, Execute, and empty testcase state. Existing
P2-S9.14-B Project Execution Insights behavior remained covered.

P2-S9.14-D was committed as `207e31e`, pushed to `origin/main`, and verified
with a clean working tree. Its verified baseline was 327 passed, 8 warnings,
and 0 failures.


---


## P2-S9.15 — Persisted Automation Artifact Identity and Traceability

**Status: COMPLETE — committed as ba9e27c and pushed to origin/main**

### Root cause

`AutomationCodeGenerationService.generate()` assigned every generated
automation artifact the ID `GA001`. The SQLite artifact repository uses
`artifact_id` as its primary key and saves with replace semantics, so distinct
artifacts could overwrite one another. This broke artifact listing and could
misassociate execution history and project reporting.

### Implementation scope

- Generate a UUID string for each new artifact inside
  `AutomationCodeGenerationService`.
- Keep the artifact model, API response shape, MCP fields, repository schema,
  replace semantics, UI behavior, and execution semantics unchanged.
- Preserve existing stored artifact IDs, including legacy `GA001` records.
- No migration or general-purpose ID framework was added.

### Validation

```text
Focused artifact/workspace/history/API tests: 30 passed, 1 warning
Focused Project Workspace browser test:        1 passed, 1 warning
Full regression suite:                         329 passed
Warnings:                                        8
Failures:                                        0
git diff --check:                                clean
```

Regression coverage verifies distinct IDs across repeated generation,
multiple artifacts persisting within and across projects, legacy `GA001`
readability, exact artifact source selection during execution, execution
history and project reporting, and browser Review/Execute selection for two
artifacts.

P2-S9.15 is complete, committed as `ba9e27c`, and pushed to `origin/main`.
P2-S9.16 — Project-Centric QA Workspace UX is complete, committed as
`6b8c532`, and pushed to `origin/main`.
