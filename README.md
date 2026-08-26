# QA MCP

QA MCP is a Model Context Protocol (MCP) server for structured software-quality workflows.

> **Current checkpoint:** P2-S8 — Automation Case Generator complete through MCP exposure and validation.
>
> **Current regression:** 151 passed, 1 known non-blocking warning.
>
> **Last committed checkpoint:** `71c893e` — Slack connector.
>
> **Next step:** P2-S8.6 — Automation Candidate Selection & QA Suite Integration.

## Project Vision

QA MCP is being developed incrementally toward an AI-assisted QA engineering platform that can understand requirements, generate and review test cases, maintain QA suites and versions, retrieve Jira/GitHub/Slack context, identify automation candidates, and eventually provide an agent/orchestrator and interactive UI.

The backend is deliberately being built first so future agent/UI layers consume stable services rather than containing business logic themselves.

## Development Principles

1. Test first.
2. Make the smallest implementation necessary to pass the test.
3. Preserve existing behavior.
4. Run focused tests after each change.
5. Run the full regression suite before advancing.
6. Keep MCP tools thin.
7. Keep business logic in core services.
8. Keep external API logic in infrastructure clients.
9. Keep LLM-specific behavior behind the LLM abstraction.
10. Use normalized Pydantic models at service boundaries.
11. Never commit real credentials.
12. Commit only after a clean regression checkpoint.
13. Update this README at meaningful phase/checkpoint boundaries.
14. Do not build the UI prematurely; stabilize agent/service contracts first.

## Current Architecture

```text
                         MCP Server
                             |
        +--------------------+--------------------+
        |                    |                    |
      QA Tools           Connectors          Automation
        |              Jira/GitHub/Slack          |
        +--------------------+--------------------+
                             |
                        Core Services
                             |
        +--------------------+--------------------+
        |                    |                    |
       LLM              Project Context       Versioning
                             |
                       Infrastructure
                             |
                    SQLite / External APIs
```

Current automation flow:

```text
MCP Tool
    |
    v
generate_automation()
    |
    | validates TestCase
    v
AutomationService
    |
    v
AutomationCaseGenerator
    |
    v
LLM
    |
    v
AutomationCaseResponse
```

The automation layer currently produces a structured automation candidate/specification, not executable Playwright/Selenium code.

## Current Capabilities

### Core QA

- Requirement analysis
- Test case generation
- Test case review
- QA suite workflow
- Project context
- SQLite persistence
- Requirement versioning
- Suite versioning
- Project import/export

### Connectors

| Connector | Status | Capabilities |
|---|---|---|
| Jira | Complete | Issue retrieval and JQL search |
| GitHub | Complete | Repository, issue, PR retrieval and issue search |
| Slack | Complete through current connector layer | Channel, messages, search, thread retrieval |
| Automation | Current phase | Structured automation candidate generation |

All connectors use abstraction/factory patterns with mock and cloud implementations.

## Connector Architecture

```text
MCP Tool
   |
Core Service
   |
Factory
   |
Abstract Client
   |
+-- Mock Client
|
+-- Cloud Client
```

Source locations:

```text
src/qa_mcp/infrastructure/jira/
src/qa_mcp/core/jira/

src/qa_mcp/infrastructure/github/
src/qa_mcp/core/github/

src/qa_mcp/infrastructure/slack/
src/qa_mcp/core/slack/
```

## Configuration

Configuration is loaded from:

```text
config/settings.yaml
```

Environment variables override YAML values. Deployment-specific secrets belong in `.env`.

Example:

```dotenv
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email
JIRA_API_TOKEN=your-token

GITHUB_URL=https://api.github.com
GITHUB_TOKEN=your-github-token
GITHUB_OWNER=your-github-username-or-org

SLACK_URL=https://slack.com/api
SLACK_TOKEN=
SLACK_DEFAULT_CHANNEL=
```

Never commit real credentials.

## Current MCP Tools

### Jira

```text
get_jira_issue
search_jira_issues
```

### GitHub

```text
get_github_repository
get_github_issue
get_github_pull_request
search_github_issues
```

### Slack

```text
get_slack_channel
get_slack_messages
search_slack_messages
get_slack_thread
```

### Automation

```text
generate_automation
```

Verify automation registration:

```bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools() if 'automation' in t.name])"
```

Expected:

```text
['generate_automation']
```

## Automation Case Generator

The current `AutomationCase` model contains:

- `id`
- `test_case_id`
- `title`
- `automation_type`
- `framework`
- `priority`
- `confidence`
- `preconditions`
- `test_data`
- `steps`
- `assertions`
- `limitations`

The generator answers:

> Given this test case, what is the appropriate way to automate it?

It does not yet generate executable automation code.

This structured intermediate representation will later support framework selection, automation code generation, feasibility/risk reporting, agent orchestration, and UI presentation.

## Error Handling

Malformed LLM JSON is rejected with:

```text
ValueError: Invalid automation generation response
```

Invalid MCP test-case input is rejected with:

```text
ValueError: Invalid test case
```

This prevents raw infrastructure/LLM/Pydantic errors from leaking through the MCP boundary.

## Testing

Run the full suite:

```bash
pytest -q
```

Current checkpoint:

```text
151 passed, 1 warning
```

The known warning is the existing `pydantic_settings` `IncompleteFieldDefinitionWarning` concerning `lifespan`. It is non-blocking and currently causes no test failures.

Focused automation tests:

```text
tests/test_automation_generator.py
tests/test_automation_case_generator.py
tests/test_automation_case_generator_errors.py
tests/test_automation_service.py
tests/test_automation_tools.py
tests/test_automation_tools_errors.py
```

## Project Structure

```text
qa-mcp/
|
+-- config/
|   +-- settings.yaml
|
+-- src/qa_mcp/
|   +-- core/
|   |   +-- automation/
|   |   +-- github/
|   |   +-- jira/
|   |   +-- slack/
|   |   +-- import_export/
|   |   +-- project/
|   |   +-- versioning/
|   |   +-- llm/
|   |
|   +-- infrastructure/
|   |   +-- github/
|   |   +-- jira/
|   |   +-- slack/
|   |   +-- versioning/
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
+-- README.md
+-- requirements.txt
+-- .env
```

## Phase History

### Foundation

- Repository initialized
- Git configuration established
- Layered architecture established
- Configuration management established
- LLM abstraction established
- Mock LLM support established
- Initial QA tools implemented

### Persistence and Versioning

- SQLite project repository
- Project context
- Requirement versioning
- Suite versioning
- Import/export support

### Jira Connector — Complete

Implemented normalized models, abstract/mock/cloud clients, service, factory, configuration, MCP tools, and tests.

### GitHub Connector — Complete

Implemented repository/issue/PR models, abstract/mock/cloud clients, service, factory, configuration, MCP tools, and tests.

### Slack Connector — Complete through current connector layer

Implemented channel/message/thread/search models, abstract/mock/cloud clients, service, factory, configuration, MCP tools, and tests.

### P2-S8 — Automation Case Generator

Completed:

- `AutomationCase` schema
- `AutomationCaseResponse` schema
- `AutomationCaseGenerator`
- malformed LLM JSON handling
- `AutomationService`
- `generate_automation` MCP tool
- invalid MCP input handling
- focused tests
- full regression validation

Current regression:

```text
151 passed, 1 warning
```

## Immediate Next Step

### P2-S8.6 — Automation Candidate Selection & QA Suite Integration

Target flow:

```text
Requirement
    |
    v
Test Cases
    |
    v
Review
    |
    v
QA Suite
    |
    v
Automation Candidate Selection
    |
    +--> Recommended for automation
    |
    +--> Manual-only
```

We should not blindly automate every generated test case.

The next objective is to define and test explicit, deterministic criteria for identifying automation candidates. The eventual output should support reporting such as:

```text
18 test cases generated
11 recommended for automation
7 remain manual
```

## Future Agent / Orchestrator

Once the underlying capabilities are stable:

```text
                         Web UI
                           |
                           v
                      QA AI Agent
                           |
                           v
                    Agent Orchestrator
                           |
          +----------------+----------------+
          |                |                |
         Jira           GitHub           Slack
          |                |                |
          +----------------+----------------+
                           |
                           v
                      QA Services
                           |
                           v
                           LLM
```

A future request could be:

```text
"Analyze the latest payment requirement and prepare
 everything needed for testing."
```

The agent could retrieve Jira context, inspect GitHub, check Slack, generate/review test cases, identify automation candidates, and prepare automation specifications.

## Future UI

The eventual product should expose real agent activity rather than a fake thinking animation.

Example:

```text
🔎 Reading Jira requirement
✓ Requirement retrieved

🧠 Analyzing acceptance criteria
✓ Acceptance criteria mapped

🐙 Checking GitHub context
✓ Related PR found

💬 Checking Slack context
✓ Relevant discussion found

🧪 Generating test cases
✓ 18 test cases

⚙️ Selecting automation candidates
✓ 11 candidates

✅ QA analysis complete
```

The UI is intentionally deferred until the service and agent contracts are stable.

## Hosting Direction

The architecture is intended for eventual cloud hosting:

```text
Browser
   |
HTTPS
   |
Web UI
   |
API / Agent Layer
   |
QA MCP / Services
   |
+--------+---------+---------+
|        |         |         |
Jira   GitHub    Slack      LLM
```

Cloud deployment, authentication, secrets management, observability and production hardening will follow the core agent capabilities.

## Local Development

Activate the environment:

```bash
source .venv/bin/activate
```

Run tests:

```bash
pytest -q
```

Verify server import:

```bash
python -c "from qa_mcp.server import mcp; print('MCP runtime import OK')"
```

Inspect automation tools:

```bash
python -c "from qa_mcp.server import mcp; print([t.name for t in mcp._tool_manager.list_tools() if 'automation' in t.name])"
```

## Git Checkpoint Discipline

Before committing:

```bash
pytest -q
git status
git diff --stat
```

Then:

```bash
git add .
git commit -m "<meaningful checkpoint message>"
git push
```

Verify:

```bash
git status
git log --oneline --decorate -5
```

Expected final state:

```text
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

## Current Git Continuity

Last committed checkpoint before the current P2-S8 work:

```text
71c893e Initial commit with Slack Configured
```

The current P2-S8 automation work is the next commit.

After committing it, update this section with the new commit hash and commit message.

## Resume Rule

When development resumes:

```bash
git status
git log --oneline --decorate -5
pytest -q
```

Then read this README.

Continue from the recorded checkpoint. Do not restart architectural decisions from scratch. Preserve the test-first, layered architecture and the established connector/service boundaries.
