from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from qa_mcp.core.automation.execution_failure_analysis_service import (
    AutomationExecutionFailureAnalysisService,
)
from qa_mcp.core.automation.candidate_selector import (
    AutomationCandidateSelector,
)
from qa_mcp.core.automation.candidate_service import (
    AutomationCandidateService,
)
from qa_mcp.core.automation.candidate_generation_service import (
    AutomationCandidateGenerationService,
)
from qa_mcp.core.automation.code_generation_service import (
    AutomationCodeGenerationService,
)
from qa_mcp.core.automation.service import (
    AutomationService,
)
from qa_mcp.tools.automation.generator import (
    AutomationCaseGenerator,
)
from qa_mcp.core.automation.execution_history_service import (
    AutomationExecutionHistoryService,
)
from qa_mcp.core.automation.execution_reporting_service import (
    AutomationExecutionReportingService,
)
from qa_mcp.core.config import load_config
from qa_mcp.core.llm import create_llm
from qa_mcp.core.project.context import ProjectContext
from qa_mcp.core.versioning.service import (
    QARequirementVersioningService,
    QASuiteVersioningService,
)
from qa_mcp.infrastructure.sqlite_project_repository import (
    SQLiteProjectRepository,
)
from qa_mcp.infrastructure.versioning.sqlite_version_repository import (
    SQLiteRequirementVersionRepository,
    SQLiteSuiteVersionRepository,
)
from qa_mcp.models.schemas import (
    QAProjectCreateRequest,
    QASuiteWorkspaceRequest,
)
from qa_mcp.tools.workflow.qa_suite import (
    QASuiteWorkflow,
)
from qa_mcp.web.qa_workspace_service import (
    QAWorkspaceService,
)


history_service = AutomationExecutionHistoryService()

reporting_service = AutomationExecutionReportingService(
    history_service
)

failure_analysis_service = (
    AutomationExecutionFailureAnalysisService()
)


# ---------------------------------------------------------
# QA Workspace
# ---------------------------------------------------------

workspace_config = load_config()

workspace_llm = create_llm(
    workspace_config
)

workspace_project_repository = (
    SQLiteProjectRepository()
)

workspace_project_context = ProjectContext(
    workspace_project_repository
)

workspace_requirement_version_repository = (
    SQLiteRequirementVersionRepository()
)

workspace_suite_version_repository = (
    SQLiteSuiteVersionRepository()
)

workspace_requirement_versioning_service = (
    QARequirementVersioningService(
        workspace_requirement_version_repository
    )
)

workspace_suite_versioning_service = (
    QASuiteVersioningService(
        workspace_suite_version_repository
    )
)

workspace_qa_suite_workflow = QASuiteWorkflow(
    workspace_llm
)

workspace_automation_case_generator = AutomationCaseGenerator(
    workspace_llm
)

workspace_automation_service = AutomationService(
    workspace_automation_case_generator
)

workspace_automation_candidate_service = (
    AutomationCandidateService(
        AutomationCandidateSelector()
    )
)

workspace_automation_candidate_generation_service = (
    AutomationCandidateGenerationService(
        candidate_service=(
            workspace_automation_candidate_service
        ),
        automation_service=(
            workspace_automation_service
        ),
    )
)

workspace_automation_code_generation_service = (
    AutomationCodeGenerationService()
)

qa_workspace_service = QAWorkspaceService(
    project_context=workspace_project_context,
    qa_suite_workflow=workspace_qa_suite_workflow,
    requirement_versioning_service=(
        workspace_requirement_versioning_service
    ),
    suite_versioning_service=(
        workspace_suite_versioning_service
    ),
    automation_candidate_service=(
        workspace_automation_candidate_service
    ),
    automation_candidate_generation_service=(
        workspace_automation_candidate_generation_service
    ),
    automation_code_generation_service=(
        workspace_automation_code_generation_service
    ),
)


app = FastAPI(
    title="QA MCP Dashboard",
    version="0.1.0",
)

app.mount(
    "/static",
    StaticFiles(
        directory="src/qa_mcp/web/static"
    ),
    name="static",
)



@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "application": "QA MCP Dashboard",
    }


# ---------------------------------------------------------
# QA Project Workspace API
# ---------------------------------------------------------

@app.get("/api/projects")
def list_qa_projects():
    return [
        project.model_dump()
        for project in qa_workspace_service.list_projects()
    ]


@app.post("/api/projects")
def create_qa_project(
    request: QAProjectCreateRequest,
):
    try:
        return qa_workspace_service.create_project(
            project_id=request.project_id,
            name=request.name,
            application=request.application,
            environment=request.environment,
            description=request.description,
            metadata=request.metadata,
        )
    except ValueError as exc:
        if "already exists" in str(exc).lower():
            raise HTTPException(
                status_code=409,
                detail=str(exc),
            ) from exc

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get("/api/projects/{project_id}")
def get_qa_project(
    project_id: str,
):
    try:
        return qa_workspace_service.get_project(
            project_id
        ).model_dump()
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/projects/{project_id}/qa-suite"
)
def generate_qa_suite(
    project_id: str,
    request: QASuiteWorkspaceRequest,
):
    try:
        return qa_workspace_service.generate_qa_suite(
            project_id=project_id,
            requirement=request.requirement,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------
# Existing Execution APIs
# ---------------------------------------------------------


@app.get("/api/executions")
def executions(
    automation_case_id: str | None = None,
    limit: int = 50,
):
    results = history_service.list(
        automation_case_id=automation_case_id,
        limit=limit,
    )

    return [
        result.model_dump()
        for result in results
    ]


@app.get("/api/executions/report")
def execution_report(
    automation_case_id: str | None = None,
):
    return reporting_service.report(
        automation_case_id=automation_case_id,
    ).model_dump()


@app.get("/api/executions/failures")
def execution_failures(
    automation_case_id: str | None = None,
    limit: int = 50,
):
    return failure_analysis_service.analyze(
        automation_case_id=automation_case_id,
        limit=limit,
    ).model_dump()


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>
<title>QA MCP Dashboard</title>
<link
    rel="stylesheet"
    href="/static/css/dashboard.css"
>


</head>

<body>

<h1>QA MCP Dashboard</h1>
<p>
    <small>
        AI-powered QA workspace and automation execution overview
    </small>
</p>


<!-- ===================================================== -->
<!-- AI QA WORKSPACE -->
<!-- ===================================================== -->

<section>

<h2>AI QA Workspace</h2>

<p>
Create a QA project and generate a complete AI-assisted
test suite from a requirement.
</p>


<h3>1. Create QA Project</h3>

<div class="workspace-grid">

    <div class="field">
        <label for="project-id">
            Project ID
        </label>

        <input
            id="project-id"
            type="text"
            placeholder="customer-portal"
        >
    </div>


    <div class="field">
        <label for="project-name">
            Project Name
        </label>

        <input
            id="project-name"
            type="text"
            placeholder="Customer Portal QA"
        >
    </div>


    <div class="field">
        <label for="project-application">
            Application
        </label>

        <input
            id="project-application"
            type="text"
            placeholder="Customer Portal"
        >
    </div>


    <div class="field">
        <label for="project-environment">
            Environment
        </label>

        <input
            id="project-environment"
            type="text"
            placeholder="test"
            value="test"
        >
    </div>
        <div class="field field-full">

            <label for="project-description">
                Description
            </label>

            <textarea
                id="project-description"
                rows="3"
                placeholder="Describe the QA project..."
            ></textarea>

        </div>

    </div>

</div>


<div style="margin-top: 16px;">

    <button
        class="primary-button"
        type="button"
        onclick="createQAProject()"
    >
        Create QA Project
    </button>

</div>


<div
    id="project-error"
    class="error"
></div>


<div
    id="project-success"
    class="success"
></div>


<h3>2. Generate QA Suite</h3>

<div class="workspace-grid">

    <div class="field field-full">

        <label for="qa-project-id">
            Project
        </label>

        <select
            id="qa-project-id"
            onchange="updateSelectedProjectId()"
        >
            <option value="">Select a project</option>
        </select>

        <div
            id="selected-project-id"
            class="success"
            style="margin-top: 8px;"
        ></div>

    </div>


    <div class="field field-full">

        <label for="qa-requirement">
            Requirement
        </label>

        <textarea
            id="qa-requirement"
            rows="6"
            placeholder="Describe the software requirement..."
        ></textarea>

    </div>

</div>


<div style="margin-top: 16px;">

    <button
        class="primary-button"
        type="button"
        onclick="generateQASuite()"
    >
        Generate QA Suite
    </button>

</div>


<div
    id="qa-workspace-error"
    class="error"
></div>


<div
    id="qa-workspace-result"
    class="result-block"
></div>

</section>


<!-- ===================================================== -->
<!-- EXISTING EXECUTION OVERVIEW -->
<!-- ===================================================== -->

<section>

<h2>Automation Execution Overview</h2>

<div class="grid">

    <div class="card">
        Total Executions
        <div
            class="value"
            id="total"
        >
            -
        </div>
    </div>


    <div class="card">
        Passed
        <div
            class="value"
            id="passed"
        >
            -
        </div>
    </div>


    <div class="card">
        Failed
        <div
            class="value"
            id="failed"
        >
            -
        </div>
    </div>


    <div class="card">
        Errors
        <div
            class="value"
            id="errors"
        >
            -
        </div>
    </div>


    <div class="card">
        Pass Rate
        <div
            class="value"
            id="pass-rate"
        >
            -
        </div>
    </div>


    <div class="card">
        Avg Duration
        <div
            class="value"
            id="avg-duration"
        >
            -
        </div>
    </div>

</div>

</section>


<section>

<h2>Recent Executions</h2>

<table>

<thead>

<tr>
<th>Execution</th>
<th>Case</th>
<th>Status</th>
<th>Duration</th>
</tr>

</thead>

<tbody id="executions-body"></tbody>

</table>

</section>


<section>

<h2>Failures</h2>

<table>

<thead>

<tr>
<th>Execution</th>
<th>Case</th>
<th>Status</th>
<th>Message</th>
</tr>

</thead>

<tbody id="failures-body"></tbody>

</table>

</section>




    <script src="/static/js/dashboard.js"></script>

</body>
</html>
        """
    )
