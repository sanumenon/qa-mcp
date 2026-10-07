# QA MCP Agent Skills Contract

## 1. Purpose

This document defines the initial capability contract for the future
QA Agent built on top of QA-MCP.

The QA Agent must use the existing QA-MCP capability layer rather than
creating duplicate business logic, persistence logic, execution logic,
or external-integration logic.

This contract is intentionally limited to capabilities that already
exist in the repository.

The contract does not itself introduce an agent runtime.

---

# 2. Contract Principles

The QA Agent must:

1. Use existing QA-MCP services and MCP tools.
2. Preserve existing Pydantic contracts.
3. Preserve existing persistence behavior.
4. Preserve existing execution safety boundaries.
5. Never bypass the controlled automation execution service.
6. Never directly manipulate SQLite persistence.
7. Never invent test cases, automation artifacts, or execution results.
8. Treat generated LLM output as untrusted until validated by existing
   application contracts.
9. Preserve requirement → test case → automation → artifact → execution
   traceability.
10. Distinguish read-only operations from mutating operations.
11. Respect existing error behavior.
12. Avoid autonomous retries unless an explicit future policy permits them.
13. Avoid destructive operations unless a future explicit capability is
    introduced.
14. Use deterministic existing services wherever possible.
15. Never weaken existing validation to satisfy an agent request.

---

# 3. Skill Status

The following status values are used:

- ACTIVE — existing capability is implemented and may be exposed to an
  agent.
- DESIGN_ONLY — capability concept exists but is not yet an agent-ready
  production boundary.
- NOT_IMPLEMENTED — capability does not currently exist.

Only ACTIVE skills are part of the initial executable agent contract.

---

# 4. Active Skills

## Skill: analyze_requirement

### Status

ACTIVE

### Purpose

Analyze a software requirement for QA test design.

### MCP Tool

`analyze_requirement`

### Classification

READ / COMPUTE ONLY

The skill does not persist a requirement.

### Required Inputs

- `requirement`

### Optional Inputs

- `application`

### Output

Structured requirement analysis.

### Existing Validation

The existing MCP tool constructs the repository's
`RequirementRequest` Pydantic contract.

### Failure Behavior

Invalid request data or LLM/provider errors must propagate through the
existing application behavior.

### Idempotency

Yes, from the persistence perspective. The operation does not create
persistent state.

### Traceability

Requirement → Requirement Analysis

---

## Skill: generate_test_cases

### Status

ACTIVE

### Purpose

Generate structured QA test cases from a software requirement.

### MCP Tool

`generate_test_cases`

### Classification

READ / COMPUTE ONLY

The MCP operation itself does not persist the generated test cases.

### Required Inputs

- `requirement`

### Optional Inputs

- `application`

### Output

Structured `TestCaseResponse`.

### Existing Validation

Generated responses are validated by the existing test-case generation
contracts.

A malformed or incomplete payload must not be accepted merely to make
generation succeed.

### Failure Behavior

Generation or validation errors must remain errors.

### Idempotency

No persistent mutation.

Repeated calls may produce different LLM output and therefore must not
be treated as deterministic unless the configured provider makes that
guarantee.

### Traceability

Requirement → Test Cases

---

## Skill: review_test_cases

### Status

ACTIVE

### Purpose

Review generated test cases against the originating requirement.

### MCP Tool

`review_test_cases`

### Classification

READ / COMPUTE ONLY

### Required Inputs

- `requirement`
- `test_cases`

### Optional Inputs

- `application`

### Output

Structured test-case review.

### Existing Validation

The supplied test cases are validated through the existing
`TestCaseResponse` contract.

### Failure Behavior

Invalid test-case payloads must be rejected.

### Idempotency

No persistent mutation.

### Traceability

Requirement → Test Cases → Test Review

---

## Skill: generate_qa_suite

### Status

ACTIVE

### Purpose

Run the existing complete QA-suite workflow:

1. requirement analysis
2. test-case generation
3. test-case review

### MCP Tool

`generate_qa_suite`

### Classification

READ / COMPUTE ONLY

The MCP operation itself does not represent selected-suite persistence.

### Required Inputs

- `requirement`

### Optional Inputs

- `application`

### Output

Structured QA suite containing:

- requirement
- analysis
- test cases
- review

### Important Constraint

The agent must not interpret this operation as equivalent to
persisting the selected suite.

Suite persistence is a separate existing capability.

### Traceability

Requirement → Analysis → Test Cases → Review

---

## Skill: create_requirement_version

### Status

ACTIVE

### Purpose

Persist an immutable requirement version for a QA project.

### MCP Tool

`create_requirement_version`

### Classification

MUTATING

### Required Inputs

- `project_id`
- `requirement`
- `application`
- `environment`

### Output

Persisted requirement version.

### Persistence

Creates an immutable requirement version using the existing versioning
service and repository.

### Idempotency

Not assumed.

The agent must not repeat this operation automatically unless the
caller explicitly intends to create another requirement version.

### Traceability

Project → Requirement Version

---

## Skill: create_suite_version

### Status

ACTIVE

### Purpose

Persist an immutable QA suite version.

### MCP Tool

`create_suite_version`

### Classification

MUTATING

### Required Inputs

- `project_id`
- `requirement_version_id`
- `test_cases`
- `review`

### Output

Persisted QA suite version.

### Existing Validation

Test cases are validated through `TestCaseResponse`.

Review is validated through `TestCaseReview`.

### Important Constraint

Only validated structured test cases may be persisted.

### Idempotency

Not assumed.

Repeated invocation may create another immutable suite version.

### Traceability

Project → Requirement Version → Suite Version → Test Cases

---

## Skill: select_automation_candidates

### Status

ACTIVE

### Purpose

Determine which test cases are suitable for automation using the
existing candidate-selection policy.

### MCP Tool

`select_automation_candidates`

### Classification

READ / COMPUTE ONLY

### Required Inputs

- `test_cases`

### Output

Structured automation-candidate result.

### Important Constraint

The agent must not replace the existing candidate-selection policy
with its own heuristic.

### Idempotency

Yes from a persistence perspective.

### Traceability

Test Cases → Automation Candidates

---

## Skill: generate_automation_for_candidates

### Status

ACTIVE

### Purpose

Generate automation cases for test cases that have been selected as
automation candidates.

### MCP Tool

`generate_automation_for_candidates`

### Classification

READ / COMPUTE ONLY

### Required Inputs

- `test_cases`

### Existing Boundary

The existing candidate-generation service controls candidate selection
and automation-case generation.

### Important Constraint

The agent must not bypass candidate selection by directly assuming
that every test case is automatable.

### Idempotency

No persistent mutation at the MCP operation boundary.

### Traceability

Test Case → Automation Candidate → Automation Case

---

## Skill: generate_automation_code

### Status

ACTIVE

### Purpose

Generate executable automation code from a validated automation case.

### MCP Tool

`generate_automation_code`

### Classification

READ / COMPUTE ONLY

### Required Inputs

- `automation_case`

### Output

`GeneratedAutomationArtifact`

### Existing Validation

The automation case is validated through the existing
`AutomationCase` contract.

### Important Constraint

Generated code must remain subject to the existing execution safety
boundary.

Generating code does not grant permission to execute it.

### Idempotency

No persistent mutation at the MCP operation boundary.

### Traceability

Automation Case → Generated Automation Artifact

---

## Skill: execute_automation_code

### Status

ACTIVE

### Purpose

Execute a generated automation artifact through the existing controlled
automation execution service.

### MCP Tool

`execute_automation_code`

### Classification

MUTATING / EXECUTION

### Required Inputs

- `artifact`

### Output

`AutomationExecutionResult`

### Security Boundary

This skill must use the existing:

`AutomationExecutionService`

It must not:

- invoke arbitrary shell commands
- bypass the controlled command builder
- bypass workspace isolation
- bypass execution timeout
- bypass framework validation
- directly execute user-provided commands

### Supported Framework

The current execution service supports:

`Playwright`

### Persistence

Execution results are persisted through the existing execution-history
service.

### Idempotency

NOT ASSUMED.

Executing the same artifact twice represents two execution attempts.

### Traceability

Automation Artifact → Execution Result

---

## Skill: get_automation_execution

### Status

ACTIVE

### Purpose

Retrieve one persisted automation execution result.

### MCP Tool

`get_automation_execution`

### Classification

READ ONLY

### Required Inputs

- `execution_id`

### Output

Persisted execution result.

### Idempotency

Yes.

### Traceability

Execution ID → Execution Result

---

## Skill: list_automation_executions

### Status

ACTIVE

### Purpose

Retrieve persisted automation execution history.

### MCP Tool

`list_automation_executions`

### Classification

READ ONLY

### Optional Inputs

- `automation_case_id`
- `limit`

### Output

List of persisted execution results.

### Idempotency

Yes.

### Traceability

Automation Case → Execution History

---

## Skill: get_automation_execution_report

### Status

ACTIVE

### Purpose

Return aggregated execution metrics.

### MCP Tool

`get_automation_execution_report`

### Classification

READ ONLY

### Optional Inputs

- `automation_case_id`

### Output

Aggregated execution report.

### Idempotency

Yes.

### Traceability

Execution History → Execution Report

---

## Skill: analyze_automation_failures

### Status

ACTIVE

### Purpose

Analyze persisted automation execution failures.

### MCP Tool

`analyze_automation_failures`

### Classification

READ ONLY / ANALYSIS

### Optional Inputs

- `automation_case_id`
- `limit`

### Output

Structured failure analysis.

### Idempotency

Yes.

### Traceability

Execution History → Failure Analysis

---

# 5. Skills Explicitly Not Active Yet

## Automation Validation

### Status

DESIGN_ONLY

The repository contains an `AutomationValidator` and dedicated tests,
but the current production workflow does not establish automation
validation as a mandatory execution boundary.

Therefore the future agent must NOT claim that:

`validate_automation`

is currently an active production skill.

The validator must first be integrated into the approved production
workflow and covered by focused and full regression tests.

---

## Scenario-Batched Test Generation

### Status

DESIGN_ONLY

The repository currently contains Bedrock output hardening, including
the larger output-token configuration.

Runtime verification is still required to determine whether
scenario-batched generation is actually necessary.

The agent must not assume that scenario batching is already implemented.

---

## Autonomous QA Orchestration

### Status

NOT_IMPLEMENTED

There is currently no production QA Agent runtime that autonomously
chains all skills.

This document defines the capability contract only.

---

## Autonomous Retry / Self-Healing

### Status

NOT_IMPLEMENTED

The agent must not autonomously retry failed LLM generation, automation
generation, or automation execution unless a future explicit policy is
implemented.

---

## CI/CD Triggering

### Status

NOT_IMPLEMENTED

The current skill contract does not authorize the agent to trigger CI/CD
pipelines.

---

# 6. Skill Invocation Rules

## Rule 1 — Validate before mutation

Before invoking a mutating skill, the agent must ensure that all required
identifiers and structured inputs are valid.

## Rule 2 — Preserve existing contracts

The agent must use the existing Pydantic and service contracts.

It must not construct alternative representations merely to bypass
validation.

## Rule 3 — Preserve traceability

The agent must retain the relationship:

Requirement
→ Requirement Version
→ Test Cases
→ Suite Version
→ Automation Candidate
→ Automation Case
→ Automation Artifact
→ Execution Result
→ Failure Analysis / Report

where those artifacts exist in the workflow.

## Rule 4 — Execution is privileged

Automation execution is a controlled operation.

The agent must never convert a generated code string into an arbitrary
shell command.

## Rule 5 — No hidden persistence

A READ / COMPUTE skill must not be assumed to persist state unless the
underlying existing implementation explicitly does so.

## Rule 6 — No duplicate business logic

Agent behavior must orchestrate existing capabilities.

It must not duplicate:

- candidate-selection logic
- automation-generation logic
- code-generation logic
- execution logic
- persistence logic
- failure-analysis logic

## Rule 7 — Errors remain visible

The agent must not suppress validation, provider, execution, or
persistence errors.

## Rule 8 — Runtime verification matters

A capability is not considered production-verified merely because the
corresponding Python function exists.

Verification must distinguish:

- source implementation
- focused test coverage
- full regression
- runtime verification

---

# 7. Initial Agent Workflow

The first future agent workflow should conceptually follow:

Requirement
    |
    v
analyze_requirement
    |
    v
generate_qa_suite
    |
    v
review / inspect generated suite
    |
    v
select_automation_candidates
    |
    v
generate_automation_for_candidates
    |
    v
generate_automation_code
    |
    v
validate execution preconditions
    |
    v
execute_automation_code
    |
    v
get_automation_execution
    |
    +------------------+
    |                  |
    v                  v
get_automation_    analyze_automation_
execution_report   failures

Persistence operations remain explicit and must not be silently inferred
from generation operations.

---

# 8. Agent Safety Rules

The initial QA Agent must NOT:

- execute arbitrary shell commands
- modify source code autonomously
- modify Git repositories autonomously
- create Jira issues autonomously
- modify GitHub repositories autonomously
- send Slack messages autonomously
- deploy applications
- modify CI/CD configuration
- delete QA artifacts
- bypass Pydantic validation
- bypass execution configuration
- bypass execution timeout
- bypass workspace isolation
- invent missing project IDs
- invent missing requirement versions
- invent execution results
- claim runtime verification without runtime evidence

---

# 9. Capability Verification Matrix

| Capability | MCP Tool | Status |
|---|---|---|
| Requirement analysis | `analyze_requirement` | ACTIVE |
| Test-case generation | `generate_test_cases` | ACTIVE |
| Test-case review | `review_test_cases` | ACTIVE |
| Complete QA suite generation | `generate_qa_suite` | ACTIVE |
| Requirement persistence | `create_requirement_version` | ACTIVE |
| Suite persistence | `create_suite_version` | ACTIVE |
| Automation candidate selection | `select_automation_candidates` | ACTIVE |
| Automation generation | `generate_automation_for_candidates` | ACTIVE |
| Automation code generation | `generate_automation_code` | ACTIVE |
| Controlled execution | `execute_automation_code` | ACTIVE |
| Execution retrieval | `get_automation_execution` | ACTIVE |
| Execution history | `list_automation_executions` | ACTIVE |
| Execution reporting | `get_automation_execution_report` | ACTIVE |
| Failure analysis | `analyze_automation_failures` | ACTIVE |
| Automation validation | — | DESIGN_ONLY |
| Scenario-batched generation | — | DESIGN_ONLY |
| Autonomous agent orchestration | — | NOT_IMPLEMENTED |
| Autonomous retry/self-healing | — | NOT_IMPLEMENTED |
| CI/CD triggering | — | NOT_IMPLEMENTED |

---

# 10. Contract Change Policy
