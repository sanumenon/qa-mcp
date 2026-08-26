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

The long-term goal is to evolve QA MCP from a collection of QA utilities into an intelligent QA agent capable of understanding requirements, generating and reviewing test cases, identifying automation candidates, generating automation, and eventually providing an interactive UI for the complete workflow.

---

## Current Checkpoint

**Phase 2 — QA Intelligence / Automation**

Current development checkpoint:

**P2-S8.7 — Automation Candidate → Automation Generation COMPLETE**

Latest verified regression:

```text
162 passed
7 warnings
0 failures
```

Current automation MCP tools:

```text
generate_automation
select_automation_candidates
generate_automation_for_candidates
```

The working tree should be committed only after updating this README together with the corresponding code and tests.

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
Automation Review / Validation
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

Automation currently follows:

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
```

The existing QA suite workflow remains separate from the new automation-candidate orchestration.

This is intentional so that new automation capabilities can evolve without destabilizing the existing QA workflow.

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

The connector is designed to support safe configuration and testable external interactions.

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

Slack was deliberately implemented behind an abstraction so cloud and mock implementations can be used independently.

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

Regression at that checkpoint:

```text
151 passed
1 warning
```

---

# 6. Automation Candidate Selection

## P2-S8.6 — COMPLETE

The system can now determine which test cases are suitable for automation.

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

This allows candidate selection to become a reusable capability for future agent workflows.

---

# 7. Candidate → Automation Generation

## P2-S8.7 — COMPLETE

The next layer connects candidate selection to automation generation.

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

The implementation also explicitly handles the zero-candidate case:

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

This provides three distinct automation capabilities:

```text
generate_automation
    → Generate automation for a known test case

select_automation_candidates
    → Identify which test cases should be automated

generate_automation_for_candidates
    → Select candidates and generate automation for them
```

---

# 8. Current Automation Architecture

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
                    /                               /                                ▼                ▼
        candidate_ids          manual_ids
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
         AutomationCase[]
```

This separation is intentional.

The candidate selector decides **what should be automated**.

The automation generator decides **how it should be automated**.

The orchestration service connects the two.

---

# 9. Current MCP Automation Surface

The current automation-related MCP surface is:

```text
generate_automation
select_automation_candidates
generate_automation_for_candidates
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
    'generate_automation_for_candidates'
]
```

---

# 10. Test Strategy

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

---

# 11. Current Test Baseline

At the current P2-S8.7 checkpoint:

```text
162 passed
7 warnings
0 failures
```

Focused automation-candidate tests:

```text
11 passed
```

The full regression suite must remain green before a phase checkpoint is committed.

---

# 12. Known Warnings

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

# 13. Configuration

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

# 14. Development Commands

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

Check Git status:

```bash
git status
```

---

# 15. Git Checkpoint History

Important development checkpoints:

```text
a288569 Initial commit with configured gitignore
1144ddd Resolve README.md merge conflict
882e149 Jira Connector Added
06dbe61 Complete GitHub connector
71c893e Initial commit with Slack Configured
169c1a1 Complete automation case generator
```

The next checkpoint should include:

```text
P2-S8.6 Automation Candidate Selection
P2-S8.7 Candidate → Automation Generation
```

together with the updated README and associated tests.

---

# 16. Next Phase

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
```

The next layer should focus on making the generated automation more useful and agent-ready.

Potential progression:

```text
AutomationCase[]
       ↓
Automation validation
       ↓
Framework-specific code generation
       ↓
Generated automation artifacts
       ↓
Automation review
       ↓
Execution integration
       ↓
Results / reporting
```

In parallel, the project can begin moving toward the eventual interactive experience:

```text
User
  ↓
QA MCP UI
  ↓
Agent / MCP orchestration
  ↓
QA capabilities
  ├── Requirement analysis
  ├── Test generation
  ├── Test review
  ├── Candidate selection
  ├── Automation generation
  ├── Jira
  ├── GitHub
  └── Slack
```

The UI and hosting layer should be introduced after the core agent capabilities are sufficiently stable.

---

# 17. Product Direction

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
Preparing QA results...
```

The intention is not merely to expose MCP tools, but to use them as the capability layer underneath an eventual agent-driven QA product.

The future UI should make the agent's progress, reasoning state, generated artifacts and results visible and understandable to the user.

---

# 18. Development Principles

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

---

# 19. Current Resume Point

**Resume from: P2-S8.8**

Previous completed checkpoints:

```text
P2-S8.6  Automation Candidate Selection       COMPLETE
P2-S8.7  Candidate → Automation Generation    COMPLETE
```

Verified baseline:

```text
162 passed
7 warnings
```

Automation MCP tools:

```text
generate_automation
select_automation_candidates
generate_automation_for_candidates
```

The next implementation should continue from this checkpoint rather than redesigning the completed candidate-selection or candidate-generation layers.
