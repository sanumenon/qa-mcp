# QA MCP

QA MCP is a Model Context Protocol (MCP) server for structured software-quality workflows.

The project is being developed incrementally using:

- Layered architecture
- Test-first development
- Pydantic-based contracts
- Persistent SQLite storage
- Immutable QA versioning
- Project import/export
- Safe external connectors
- MCP tool boundaries
- LLM-assisted QA analysis and automation generation

The long-term goal is to evolve QA MCP from a collection of QA utilities into an intelligent QA agent capable of understanding requirements, generating and reviewing test cases, identifying automation candidates, generating automation code, validating generated artifacts, executing automation, and eventually providing an interactive UI for the complete workflow.

---

## Current Checkpoint

**Phase 2 — QA Intelligence / Automation**

Current development checkpoint:

**P2-S8.8 — Automation Validation + Code Generation COMPLETE**

Latest verified regression:

```text
180 passed
7 warnings
0 failures
```

Current automation MCP tools:

```text
generate_automation
select_automation_candidates
generate_automation_for_candidates
generate_automation_code
```

The working tree should be committed only after updating this README together with the corresponding code and tests.

Checkpoint discipline:

```text
P2-S8.8 COMPLETE
    ↓
Commit code + tests + README
    ↓
Push to GitHub
    ↓
P2-S8.9 Automation Execution
```

The repository must remain at a clean, reproducible checkpoint before the next implementation begins.


---

# 1. Project Vision

QA MCP is intended to become a reusable QA intelligence platform rather than a simple test-case generator.

The intended evolution is:

```text
Requirement
    ↓
Requirement Analysis
    ↓
Test Case Generation
    ↓
Test Case Review
    ↓
Automation Candidate Selection
    ↓
Automation Generation
    ↓
Automation Validation
    ↓
Automation Code Generation
    ↓
Execution / Reporting
    ↓
Agent-driven QA workflow
    ↓
Interactive Web UI
```

External systems such as Jira, GitHub and Slack provide additional context to the QA agent.

---

# 2. Current Architecture

The project follows a layered architecture:

```text
MCP / Server Layer
        │
        ▼
Core Services
        │
        ▼
Domain / Models
        │
        ▼
Infrastructure
        │
        ├── SQLite
        ├── Jira
        ├── GitHub
        └── Slack
```

The automation pipeline now follows:

```text
TestCase[]
    │
    ▼
AutomationCandidateSelector
    │
    ▼
AutomationCandidateService
    │
    ▼
AutomationCandidateResult
    │
    ▼
AutomationCandidateGenerationService
    │
    ▼
AutomationService
    │
    ▼
AutomationCase[]
    │
    ▼
AutomationValidator
    │
    ▼
AutomationValidationResult
    │
    ▼
AutomationCodeGenerationService
    │
    ▼
GeneratedAutomationArtifact
```

The existing QA suite workflow remains separate from the automation-candidate orchestration.

This is intentional so that automation capabilities can evolve without destabilizing the existing QA workflow.

---

# 3. Completed Capabilities

## 3.1 Requirement Analysis

The system supports structured requirement analysis including:

- Actors
- Functional requirements
- Business rules
- Preconditions
- Main workflows
- Positive scenarios
- Negative scenarios
- Edge cases
- Missing information
- Recommended test types

---

## 3.2 Test Case Generation

The system supports structured test case generation from analyzed requirements.

Current test case model includes:

- ID
- Title
- Test type
- Priority
- Preconditions
- Steps
- Expected result

---

## 3.3 Test Case Review

Generated test suites can be reviewed for:

- Overall quality
- Coverage
- Duplicate test cases
- Missing scenarios
- Weak test cases
- Requirement gaps
- Priority issues
- Recommendations
- Summary

---

# 4. External Connectors

## Jira Connector

Jira integration has been implemented with a layered design:

```text
Jira Service
    ↓
Jira Client
    ↓
Jira Cloud Client / Mock Client
```

Git checkpoint:

```text
882e149 Jira Connector Added
```

---

## GitHub Connector

GitHub integration has been implemented with support for structured repository, issue and pull-request interactions.

Git checkpoint:

```text
06dbe61 Complete GitHub connector
```

---

## Slack Connector

Slack integration has been implemented with:

- Slack configuration
- Slack client
- Slack cloud client
- Slack mock client
- Slack service
- Slack factory
- MCP tools

Current Slack MCP tools:

```text
get_slack_channel
get_slack_messages
search_slack_messages
get_slack_thread
```

Git checkpoint:

```text
71c893e Initial commit with Slack Configured
```

---

# 5. Automation Generation

The first automation-generation capability has been implemented.

The automation generator accepts a structured `TestCase` and produces an `AutomationCase`.

The current automation model contains:

- Automation ID
- Source test case ID
- Title
- Automation type
- Framework
- Priority
- Confidence
- Preconditions
- Test data
- Steps
- Assertions
- Limitations

Current MCP tool:

```text
generate_automation
```

The implementation includes validation of invalid LLM responses.

Git checkpoint:

```text
169c1a1 Complete automation case generator
```

---

# 6. Automation Candidate Selection

## P2-S8.6 — COMPLETE

The system can determine which test cases are suitable for automation.

The candidate selector separates test cases into:

```text
Automation candidates
Manual-only candidates
```

The structured result is:

```text
AutomationCandidateResult
```

with:

- `candidate_ids`
- `manual_ids`
- `total`

Current MCP tool:

```text
select_automation_candidates
```

The candidate-selection implementation is intentionally independent of the existing QA suite workflow.

---

# 7. Candidate → Automation Generation

## P2-S8.7 — COMPLETE

The orchestration service is:

```text
AutomationCandidateGenerationService
```

Its responsibility is deliberately narrow:

```text
TestCase[]
    ↓
Candidate Selection
    ↓
candidate_ids
    ↓
Generate automation ONLY for candidates
    ↓
AutomationCase[]
```

Manual-only test cases are not sent to the automation generator.

The zero-candidate case is explicitly handled:

```text
No automation candidates
        ↓
[]
        ↓
Automation generator is NOT called
```

Current MCP tool:

```text
generate_automation_for_candidates
```

The three capabilities established by P2-S8.6/P2-S8.7 are:

```text
generate_automation
    → Generate automation for a known test case

select_automation_candidates
    → Identify which test cases should be automated

generate_automation_for_candidates
    → Select candidates and generate automation for them
```

---

# 8. Automation Validation

## P2-S8.8 — VALIDATION LAYER COMPLETE

Generated `AutomationCase` objects can now be validated before code generation.

The validation result is:

```text
AutomationValidationResult
```

with:

- `automation_case_id`
- `test_case_id`
- `valid`
- `errors`
- `warnings`

The validator currently enforces the following minimum requirements:

```text
Automation case must contain at least one step
Automation case must contain at least one assertion
Automation case must specify a framework
```

Validation is intentionally kept as a separate service:

```text
AutomationCase
      ↓
AutomationValidator
      ↓
AutomationValidationResult
```

This keeps validation independent from generation and code generation.

---

# 9. Automation Code Generation

## P2-S8.8 — COMPLETE

The next layer converts a validated automation case into a structured executable automation artifact.

The service is:

```text
AutomationCodeGenerationService
```

The current implementation generates:

```text
Python
+
Playwright
```

The generated artifact is represented by:

```text
GeneratedAutomationArtifact
```

with:

- `id`
- `automation_case_id`
- `framework`
- `language`
- `file_name`
- `code`

The current code-generation flow is:

```text
AutomationCase
      ↓
Validation checks
      ↓
AutomationCodeGenerationService
      ↓
Python / Playwright code
      ↓
GeneratedAutomationArtifact
```

The generated code currently provides a structured Playwright test function and preserves the source automation steps and assertions as code comments.

The service rejects:

- automation cases without steps
- automation cases without assertions
- automation cases without a framework
- unsupported automation frameworks

The current supported framework is:

```text
Playwright
```

The generated artifact uses:

```text
Language: Python
Framework: Playwright
```

Example generated artifact metadata:

```text
id: GA001
automation_case_id: AC001
framework: Playwright
language: Python
file_name: test_successful_login.py
```

This layer deliberately does not yet attempt to provide a complete production-grade locator strategy. That will be addressed in a later checkpoint after the structured generation pipeline is stable.

---

# 10. Current Automation Architecture

The complete current automation flow is:

```text
                         TestCase[]
                             │
                             ▼
              ┌─────────────────────────────┐
              │ AutomationCandidateSelector │
              └──────────────┬──────────────┘
                             │
                             ▼
                AutomationCandidateService
                             │
                             ▼
                   AutomationCandidateResult
                        /             \
                       /               \
              candidate_ids         manual_ids
                   │
                   ▼
       AutomationCandidateGenerationService
                   │
                   ▼
            AutomationService
                   │
                   ▼
        AutomationCaseGenerator
                   │
                   ▼
             AutomationCase
                   │
                   ▼
          AutomationValidator
                   │
                   ▼
       AutomationValidationResult
                   │
                   ▼
    AutomationCodeGenerationService
                   │
                   ▼
      GeneratedAutomationArtifact
```

The separation remains intentional:

- Candidate selection decides **what should be automated**.
- Automation generation decides **how it should be represented as an automation case**.
- Validation decides **whether the automation case is structurally acceptable**.
- Code generation decides **how to produce an executable automation artifact**.
- MCP tools remain thin orchestration boundaries.

---

# 11. Current MCP Automation Surface

The current automation-related MCP surface is:

```text
generate_automation
select_automation_candidates
generate_automation_for_candidates
generate_automation_code
```

Verified using:

```bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools() if 'automation' in t.name])"
```

Expected:

```text
[
    'generate_automation',
    'select_automation_candidates',
    'generate_automation_for_candidates',
    'generate_automation_code'
]
```

---

# 12. Test Strategy

The project uses test-first development.

New capabilities are introduced by:

```text
Write failing test
        ↓
Implement smallest production change
        ↓
Run focused test
        ↓
Run related tests
        ↓
Run full regression
        ↓
Update README
        ↓
Commit code + tests + README
```

This approach is being maintained throughout Phase 2.

P2-S8.8 added focused coverage for:

```text
GeneratedAutomationArtifact
AutomationCodeGenerationService
Empty / invalid automation cases
generate_automation_code MCP tool
```

---

# 13. Current Test Baseline

At the current P2-S8.8 checkpoint:

```text
180 passed
7 warnings
0 failures
```

The automation code-generation focused tests are green.

The full regression suite must remain green before a phase checkpoint is committed.

---

# 14. Known Warnings

There are currently two categories of non-blocking warnings.

## Pytest Collection Warnings

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

They can be cleaned up later through test-only import aliases.

---

## Pydantic Settings Warning

There is also an existing warning related to the `lifespan` forward reference:

```text
IncompleteFieldDefinitionWarning
```

The warning originates from:

```text
pydantic_settings
```

and does not currently cause test failures.

This should be treated as separate technical debt rather than mixed into the automation feature work.

---

# 15. Configuration

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

# 16. Development Commands

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

Check all MCP tools:

```bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools()])"
```

Check automation tools:

```bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools() if 'automation' in t.name])"
```

Check Git status:

```bash
git status
```

Inspect staged changes before committing:

```bash
git diff --cached --stat
git diff --cached
```

---

# 17. Git Checkpoint History

Important development checkpoints:

```text
a288569 Initial commit with configured gitignore
1144ddd Resolve README.md merge conflict
882e149 Jira Connector Added
06dbe61 Complete GitHub connector
71c893e Initial commit with Slack Configured
169c1a1 Complete automation case generator
1d2360b Add automation candidate pipeline
```

Completed automation checkpoints:

```text
P2-S8.6  Automation Candidate Selection
P2-S8.7  Candidate → Automation Generation
P2-S8.8  Automation Validation + Code Generation
```

Each completed checkpoint must include:

```text
Production code
Tests
README update
```

---

# 18. Next Phase

The next development step should build on the now-established automation pipeline.

Current capability:

```text
Requirement
    ↓
Test Cases
    ↓
Candidate Selection
    ↓
Automation Generation
    ↓
Automation Validation
    ↓
Automation Code Generation
    ↓
Generated Automation Artifact
```

The next layer should make the generated automation more useful and agent-ready.

Planned progression:

```text
GeneratedAutomationArtifact
        ↓
Artifact Review
        ↓
Framework-specific improvements
        ↓
Locator / selector strategy
        ↓
Execution integration
        ↓
Execution results
        ↓
Evidence / reporting
        ↓
Agent-driven QA workflow
```

The project should continue incrementally rather than combining execution, reporting, UI, and code-generation sophistication into a single checkpoint.

---

# 19. Product Direction

The eventual product should provide an experience where a user can submit a requirement and see the QA agent work through the process:

```text
Understanding requirement...
        ↓
Analyzing scenarios...
        ↓
Generating test cases...
        ↓
Reviewing coverage...
        ↓
Identifying automation candidates...
        ↓
Generating automation...
        ↓
Validating automation...
        ↓
Generating automation code...
        ↓
Executing automation...
        ↓
Preparing QA results...
```

The intention is not merely to expose MCP tools, but to use them as the capability layer underneath an eventual agent-driven QA product.

The future UI should make the agent's progress, generated artifacts and results visible and understandable to the user.

---

# 20. Development Principles

The following principles should remain unchanged as the project grows:

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
12. Do not redesign completed layers unless a new requirement requires it.
13. Preserve the checkpoint history so development can always resume from a known state.

---

# 21. Current Resume Point

**Resume from: P2-S8.9 — Automation Execution**

Previous completed checkpoints:

```text
P2-S8.6  Automation Candidate Selection       COMPLETE
P2-S8.7  Candidate → Automation Generation    COMPLETE
P2-S8.8  Automation Validation + Code Generation COMPLETE
```

Verified baseline:

```text
180 passed
7 warnings
0 failures
```

Current automation MCP tools:

```text
generate_automation
select_automation_candidates
generate_automation_for_candidates
generate_automation_code
```

The next implementation should continue from **P2-S8.9** rather than redesigning the completed candidate-selection, automation-generation, validation, or code-generation layers.

The established pipeline is now:

```text
TestCase
   ↓
Candidate Selection
   ↓
AutomationCase
   ↓
Validation
   ↓
GeneratedAutomationArtifact
```

This pipeline is the baseline for the next development checkpoint.
