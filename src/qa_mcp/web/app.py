from __future__ import annotations

import logging
import secrets
import time

from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse, PlainTextResponse

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
from qa_mcp.core.automation.execution_service import (
    AutomationExecutionService,
)
from qa_mcp.core.automation.execution_reporting_service import (
    AutomationExecutionReportingService,
)
from qa_mcp.core.config import load_config
from qa_mcp.core.llm import (
    LLMGenerationError,
    create_llm,
)
from qa_mcp.core.project.context import ProjectContext
from qa_mcp.core.security.authorization import ProjectAuthorization
from qa_mcp.infrastructure.sqlite_authorization_repository import (
    SQLiteAuthorizationRepository,
)
from qa_mcp.infrastructure.sqlite_qa_workspace_artifact_repository import (
    SQLiteQAWorkspaceArtifactRepository,
)
from qa_mcp.web.auth import install_authentication_middleware, install_auth_exception_handler
from qa_mcp.core.security.oidc import GoogleOIDCProvider
from qa_mcp.core.security.actor import current_actor
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
    QAProjectAutomationGenerationRequest,
    QAProjectCreateRequest,
    QASuiteSaveRequest,
    QASuiteWorkspaceRequest,
)
from qa_mcp.tools.workflow.qa_suite import (
    QASuiteWorkflow,
)
from qa_mcp.web.qa_workspace_service import (
    QAWorkspaceService,
)


logger = logging.getLogger(__name__)

workspace_config = load_config()
auth_settings = dict(workspace_config["auth"])
auth_settings["environment"] = workspace_config["application"]["environment"]
auth_settings["backup_directory"] = workspace_config["database"]["backup_directory"]
auth_settings["backup_retention"] = workspace_config["database"]["backup_retention"]

if auth_settings["mode"] == "google":
    required_google_settings = (
        "google_client_id",
        "google_client_secret",
        "redirect_uri",
        "workspace_domain",
        "session_secret",
    )
    missing_google_settings = [
        key for key in required_google_settings if not auth_settings.get(key)
    ]
    if missing_google_settings:
        raise RuntimeError(
            "Google OIDC configuration is incomplete: "
            + ", ".join(missing_google_settings)
        )
    if len(auth_settings["session_secret"]) < 32:
        raise RuntimeError("QA_SESSION_SECRET must contain at least 32 characters")
    oidc_provider = GoogleOIDCProvider(auth_settings)
else:
    oidc_provider = None

history_service = AutomationExecutionHistoryService()

reporting_service = AutomationExecutionReportingService(
    history_service
)

failure_analysis_service = (
    AutomationExecutionFailureAnalysisService()
)

workspace_automation_execution_service = (
    AutomationExecutionService()
)
workspace_artifact_repository = SQLiteQAWorkspaceArtifactRepository()


# ---------------------------------------------------------
# QA Workspace
# ---------------------------------------------------------

workspace_llm = create_llm(
    workspace_config
)

workspace_project_repository = (
    SQLiteProjectRepository()
)

authorization_repository = SQLiteAuthorizationRepository(
    database_path=workspace_config["database"]["path"],
    legacy_ownership=auth_settings["legacy_project_owners"],
)
project_authorization = ProjectAuthorization(
    authorization_repository,
    auth_settings["global_admin_subjects"],
)

workspace_project_context = ProjectContext(
    workspace_project_repository,
    authorization=project_authorization,
)

workspace_requirement_version_repository = (
    SQLiteRequirementVersionRepository()
)

workspace_suite_version_repository = (
    SQLiteSuiteVersionRepository()
)

workspace_requirement_versioning_service = (
    QARequirementVersioningService(
        workspace_requirement_version_repository,
        authorization=project_authorization,
    )
)

workspace_suite_versioning_service = (
    QASuiteVersioningService(
        workspace_suite_version_repository,
        requirement_repository=workspace_requirement_version_repository,
        authorization=project_authorization,
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
    workspace_artifact_repository=workspace_artifact_repository,
    automation_execution_service=(
        workspace_automation_execution_service
    ),
    automation_execution_history_service=(
        history_service
    ),
)


app = FastAPI(
    title="QA MCP Dashboard",
    version="0.1.0",
)

install_authentication_middleware(
    app, auth_settings, project_authorization, authorization_repository
)
install_auth_exception_handler(app)

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


@app.get("/health/live")
def liveness():
    return {"status": "alive", "application": "QA MCP Dashboard"}


@app.get("/api/ready")
def readiness():
    ready = authorization_repository.database_ready()
    unmapped_count = len(authorization_repository.unmapped_project_ids())
    return JSONResponse(
        {
            "status": "ready" if ready and unmapped_count == 0 else "not_ready",
            "checks": {
                "database": "ok" if ready else "unavailable",
                "legacy_project_ownership": "ok" if unmapped_count == 0 else "mapping_required",
            },
            "unmapped_legacy_project_count": unmapped_count,
        },
        status_code=200 if ready and unmapped_count == 0 else 503,
    )


@app.get("/api/auth/me")
def authenticated_identity():
    actor = current_actor()
    return {
        "subject": actor.subject,
        "email": actor.email,
        "authenticated": actor.authenticated,
        "global_admin": project_authorization.is_global_admin(actor),
    }


@app.get("/auth/login")
async def login(request: Request):
    if auth_settings["mode"] == "development":
        return RedirectResponse("/")
    try:
        return await oidc_provider.begin(request)
    except Exception:
        logger.warning("Google OIDC login initiation failed")
        return PlainTextResponse("Authentication could not be started", status_code=503)


@app.get("/auth/callback")
async def auth_callback(request: Request):
    if oidc_provider is None:
        return PlainTextResponse("Google authentication is disabled", status_code=404)
    try:
        actor = await oidc_provider.complete(request)
        request.session.clear()
        request.session.update(
            {
                "actor_sub": actor.subject,
                "actor_email": actor.email,
                "expires_at": time.time() + auth_settings["session_max_age_seconds"],
                "csrf_token": secrets.token_urlsafe(32),
            }
        )
        return RedirectResponse("/", status_code=303)
    except Exception:
        request.session.clear()
        logger.warning("Google OIDC callback rejected")
        return PlainTextResponse("Google authentication failed", status_code=401)


@app.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    response = JSONResponse({"status": "signed_out"})
    response.delete_cookie("qa_session", path="/")
    response.delete_cookie("qa_csrf", path="/")
    return response


@app.post("/api/projects/{project_id}/members")
def add_project_member(project_id: str, request: dict):
    actor_id = request.get("actor_id")
    if not isinstance(actor_id, str) or not actor_id.strip():
        raise HTTPException(status_code=400, detail="actor_id is required")
    project_authorization.grant_member(project_id, actor_id.strip())
    return {"project_id": project_id, "actor_id": actor_id.strip(), "role": "project_member"}


@app.delete("/api/projects/{project_id}/members/{actor_id}")
def remove_project_member(project_id: str, actor_id: str):
    if not project_authorization.is_global_admin():
        raise HTTPException(status_code=403, detail="Project administration denied")
    project_authorization.require_project(project_id)
    removed = authorization_repository.revoke_project_member(project_id, actor_id)
    return {"project_id": project_id, "actor_id": actor_id, "removed": removed}


def _authorized_artifact_ids() -> list[str] | None:
    project_ids = project_authorization.visible_project_ids()
    if project_ids is None:
        return None
    artifact_ids: list[str] = []
    for project_id in project_ids:
        artifact_ids.extend(
            workspace_artifact_repository.list_artifact_ids_for_project(project_id)
        )
    return artifact_ids


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


@app.get(
    "/api/projects/{project_id}/workspace"
)
def get_qa_project_workspace(
    project_id: str,
):
    try:
        return (
            qa_workspace_service
            .get_project_qa_workspace(
                project_id
            )
        )
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
    except LLMGenerationError as exc:
        if exc.provider_response:
            logger.error(
                "Bedrock LLM provider failure: %s",
                exc.provider_response,
            )
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

@app.post(
    "/api/projects/{project_id}/automation"
)
def generate_project_automation(
    project_id: str,
    request: QAProjectAutomationGenerationRequest,
):
    try:
        return (
            qa_workspace_service
            .generate_automation_from_project(
                project_id=project_id,
                selected_test_case_ids=(
                    request.selected_test_case_ids
                ),
            )
        )
    except ValueError as exc:
        message = str(exc)

        if (
            "not found" in message.lower()
            or "unknown test case" in message.lower()
        ):
            status_code = 404
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc


@app.post(
    "/api/projects/{project_id}/automation/{artifact_id}/execute"
)
def execute_project_automation(
    project_id: str,
    artifact_id: str,
):
    try:
        return qa_workspace_service.execute_project_automation(
            project_id=project_id,
            artifact_id=artifact_id,
        )
    except ValueError as exc:
        message = str(exc)

        if "not found" in message.lower():
            status_code = 404
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc


@app.post(
    "/api/projects/{project_id}/qa-suite/save"
)
def save_qa_suite(
    project_id: str,
    request: QASuiteSaveRequest,
):
    try:
        return qa_workspace_service.save_selected_test_cases(
            project_id=project_id,
            requirement_version_id=(
                request.requirement_version_id
            ),
            test_cases=request.test_cases.model_dump(),
            review=request.review.model_dump(),
            selected_test_case_ids=(
                request.selected_test_case_ids
            ),
        )
    except ValueError as exc:
        message = str(exc)

        if (
            "not found" in message.lower()
            or "unknown test case" in message.lower()
        ):
            status_code = 404
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc


@app.get("/api/projects/{project_id}/executions")
def project_executions(
    project_id: str,
    limit: int = 50,
):
    try:
        results = qa_workspace_service.list_project_executions(
            project_id=project_id,
            limit=limit,
        )

        return [
            result.model_dump()
            for result in results
        ]
    except ValueError as exc:
        message = str(exc)

        if (
            "not found" in message.lower()
            or "unknown project" in message.lower()
        ):
            status_code = 404
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc


@app.get("/api/projects/{project_id}/executions/report")
def project_execution_report(
    project_id: str,
):
    try:
        return qa_workspace_service.project_execution_report(
            project_id=project_id,
        ).model_dump()
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@app.get("/api/projects/{project_id}/executions/failures")
def project_execution_failures(
    project_id: str,
    limit: int = 50,
):
    try:
        return qa_workspace_service.project_execution_failures(
            project_id=project_id,
            limit=limit,
        ).model_dump()
    except ValueError as exc:
        message = str(exc)

        if (
            "not found" in message.lower()
            or "unknown project" in message.lower()
        ):
            status_code = 404
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc


@app.get(
    "/api/projects/{project_id}/executions/{execution_id}"
)
def project_execution_detail(
    project_id: str,
    execution_id: str,
):
    try:
        result = qa_workspace_service.get_project_execution(
            project_id=project_id,
            execution_id=execution_id,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Execution not found: {execution_id}"
                ),
            )

        return result.model_dump()
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
    artifact_ids = _authorized_artifact_ids()
    results = (
        history_service.list(
            automation_case_id=automation_case_id,
            limit=limit,
        )
        if artifact_ids is None
        else history_service.repository.list_for_artifact_ids(
            artifact_ids, limit=limit, automation_case_id=automation_case_id
        )
    )

    return [
        result.model_dump()
        for result in results
    ]


@app.get("/api/executions/report")
def execution_report(
    automation_case_id: str | None = None,
):
    artifact_ids = _authorized_artifact_ids()
    result = (
        reporting_service.report(automation_case_id=automation_case_id)
        if artifact_ids is None
        else history_service.repository.report_for_artifact_ids(
            artifact_ids, automation_case_id=automation_case_id
        )
    )
    return result.model_dump()


@app.get("/api/executions/failures")
def execution_failures(
    automation_case_id: str | None = None,
    limit: int = 50,
):
    artifact_ids = _authorized_artifact_ids()
    result = (
        failure_analysis_service.analyze(
            automation_case_id=automation_case_id, limit=limit
        )
        if artifact_ids is None
        else failure_analysis_service.repository.analyze_failures_for_artifact_ids(
            artifact_ids, limit=limit, automation_case_id=automation_case_id
        )
    )
    return result.model_dump()

# ---------------------------------------------------------
# Workflow Pages
# ---------------------------------------------------------


@app.get(
    "/execution",
    response_class=HTMLResponse,
)
def execution_page():
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

<title>QA MCP — Execution</title>

<link
    rel="stylesheet"
    href="/static/css/dashboard.css"
>

</head>

<body>

<nav class="workflow-navigation">

    <a
        class="workflow-nav-link"
        href="/"
    >
        Dashboard
    </a>

    <a
        class="workflow-nav-link"
        href="/project-workspace"
    >
        Projects / QA Workspace
    </a>

    <a
        class="workflow-nav-link active"
        href="/execution"
    >
        Execution
    </a>

    <a
        class="workflow-nav-link"
        href="/reports"
    >
        Reports &amp; Analysis
    </a>

</nav>

<main>

<section>

<h1>Execution</h1>

<p>
Review automation execution history and execution details
without changing execution behavior.
</p>

<div
    id="execution-error"
    class="error"
></div>

<div class="grid">

    <div class="card">
        Total Executions
        <div
            class="value"
            id="execution-total"
        >
            -
        </div>
    </div>

    <div class="card">
        Passed
        <div
            class="value"
            id="execution-passed"
        >
            -
        </div>
    </div>

    <div class="card">
        Failed
        <div
            class="value"
            id="execution-failed"
        >
            -
        </div>
    </div>

    <div class="card">
        Errors
        <div
            class="value"
            id="execution-errors"
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
<th>Automation Case</th>
<th>Status</th>
<th>Duration</th>
</tr>

</thead>

<tbody id="execution-body"></tbody>

</table>

</section>

</main>

<script src="/static/js/auth.js"></script>
<script src="/static/js/execution.js"></script>

</body>

</html>
"""
    )


@app.get(
    "/reports",
    response_class=HTMLResponse,
)
def reports_page():
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

<title>QA MCP — Reports &amp; Analysis</title>

<link
    rel="stylesheet"
    href="/static/css/dashboard.css"
>

</head>

<body>

<nav class="workflow-navigation">

    <a
        class="workflow-nav-link"
        href="/"
    >
        Dashboard
    </a>

    <a
        class="workflow-nav-link"
        href="/project-workspace"
    >
        Projects / QA Workspace
    </a>

    <a
        class="workflow-nav-link"
        href="/execution"
    >
        Execution
    </a>

    <a
        class="workflow-nav-link active"
        href="/reports"
    >
        Reports &amp; Analysis
    </a>

</nav>

<main>

<section>

<h1>Reports &amp; Analysis</h1>

<p>
Review aggregate execution reporting and failure analysis
using the existing backend capabilities.
</p>

<div
    id="reports-error"
    class="error"
></div>

<div class="grid">

    <div class="card">
        Total Executions
        <div
            class="value"
            id="report-total"
        >
            -
        </div>
    </div>

    <div class="card">
        Pass Rate
        <div
            class="value"
            id="report-pass-rate"
        >
            -
        </div>
    </div>

    <div class="card">
        Average Duration
        <div
            class="value"
            id="report-average-duration"
        >
            -
        </div>
    </div>

</div>

</section>


<section>

<h2>Failure Analysis</h2>

<table>

<thead>

<tr>
<th>Execution</th>
<th>Automation Case</th>
<th>Status</th>
<th>Message</th>
</tr>

</thead>

<tbody id="failure-body"></tbody>

</table>

</section>

</main>

<script src="/static/js/auth.js"></script>
<script src="/static/js/reports.js"></script>

</body>

</html>
"""
    )

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
<nav class="workflow-navigation">

    <a
        class="workflow-nav-link active"
        href="/"
    >
        Dashboard
    </a>

    <a
        class="workflow-nav-link"
        href="/project-workspace"
    >
        Projects / QA Workspace
    </a>

    <a
        class="workflow-nav-link"
        href="/execution"
    >
        Execution
    </a>

    <a
        class="workflow-nav-link"
        href="/reports"
    >
        Reports &amp; Analysis
    </a>

</nav>
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
        id="create-qa-project-button"
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
        <a
            id="open-project-workspace-link"
            class="secondary-button project-workspace-link"
            href="/project-workspace"
            hidden
        >
            Open Project Workspace
        </a>

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
        id="generate-qa-suite-button"
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




    <script src="/static/js/auth.js"></script>
    <script src="/static/js/dashboard.js"></script>

</body>
</html>
        """
    )

@app.get(
    "/project-workspace",
    response_class=HTMLResponse,
)
def project_workspace():
    return """
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>Project QA Workspace</title>

<link
    rel="stylesheet"
    href="/static/css/dashboard.css"
>

</head>

<body>

<nav class="workflow-navigation">

    <a
        class="workflow-nav-link"
        href="/"
    >
        Dashboard
    </a>

    <a
        class="workflow-nav-link active"
        href="/project-workspace"
    >
        Projects / QA Workspace
    </a>

    <a
        class="workflow-nav-link"
        href="/execution"
    >
        Execution
    </a>

    <a
        class="workflow-nav-link"
        href="/reports"
    >
        Reports &amp; Analysis
    </a>

</nav>

<main>

<section>

<h1>Project QA Workspace</h1>

<p>
View requirements, saved test cases, suite versions,
automation candidates, and generated automation artifacts
already prepared for the selected project.
</p>

<div class="workspace-grid">

    <div class="field field-full">

        <label for="repository-project-id">
            Project
        </label>

        <select id="repository-project-id" onchange="selectProjectWorkspace()">

            <option value="">
                Select a project
            </option>

        </select>

    </div>

</div>

<div style="margin-top: 16px;">

    <button
        id="load-project-workspace-button"
        class="primary-button"
        type="button"
        onclick="loadProjectQAWorkspace()"
    >
        Load Project Workspace
    </button>

</div>

<div
    id="project-workspace-error"
    class="error"
></div>

<div id="project-workspace-action-mount">
    <div
        id="project-workspace-action"
        style="margin-top: 16px;"
        hidden
    >
        <button
            id="generate-project-automation-button"
            class="primary-button"
            type="button"
            onclick="generateProjectAutomation()"
            disabled
        >
            Generate Automation for Selected Candidates
        </button>
    </div>
</div>

<div
    id="project-workspace-result"
    class="result-block"
></div>

<div id="project-workspace-notice" class="success" role="status" aria-live="polite"></div>

<section
    id="project-area-executions"
    class="project-area-panel"
    role="tabpanel"
    tabindex="0"
    hidden
>
<div
    id="project-execution-history"
    class="result-block"
></div>

<div
    id="project-execution-review"
    class="result-block"
></div>
</section>

<section
    id="project-area-reports"
    class="project-area-panel"
    role="tabpanel"
    tabindex="0"
    hidden
>
    <div
        id="project-execution-insights"
        class="result-block project-execution-insights"
        aria-live="polite"
    >
        <h3>Project Execution Insights</h3>
        <p>
            Select a project and load its workspace to view
            project-scoped execution metrics and failures.
        </p>
    </div>
</section>

</section>

</main>

<script src="/static/js/auth.js"></script>
<script src="/static/js/project_workspace.js"></script>

</body>

</html>
"""
