from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from qa_mcp.core.automation.execution_history_service import (
    AutomationExecutionHistoryService,
)
from qa_mcp.core.automation.execution_reporting_service import (
    AutomationExecutionReportingService,
)
from qa_mcp.core.automation.execution_failure_analysis_service import (
    AutomationExecutionFailureAnalysisService,
)


history_service = AutomationExecutionHistoryService()
reporting_service = AutomationExecutionReportingService(
    history_service
)
failure_analysis_service = (
    AutomationExecutionFailureAnalysisService()
)


app = FastAPI(
    title="QA MCP Dashboard",
    version="0.1.0",
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "application": "QA MCP Dashboard",
    }


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


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QA MCP Dashboard</title>
<style>
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 24px;
    background: #f5f7fb;
    color: #1f2937;
}
h1 {
    margin-top: 0;
}
.grid {
    display: grid;
    grid-template-columns: repeat(
        auto-fit,
        minmax(160px, 1fr)
    );
    gap: 16px;
    margin-bottom: 24px;
}
.card {
    background: white;
    border-radius: 10px;
    padding: 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.value {
    font-size: 28px;
    font-weight: bold;
    margin-top: 8px;
}
section {
    background: white;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
table {
    width: 100%;
    border-collapse: collapse;
}
th, td {
    text-align: left;
    padding: 10px;
    border-bottom: 1px solid #e5e7eb;
}
.status-PASSED {
    font-weight: bold;
}
.status-FAILED,
.status-ERROR {
    font-weight: bold;
}
small {
    color: #6b7280;
}
</style>
</head>
<body>

<h1>QA MCP Dashboard</h1>
<p><small>Automation execution overview</small></p>

<div class="grid">
    <div class="card">
        Total Executions
        <div class="value" id="total">-</div>
    </div>
    <div class="card">
        Passed
        <div class="value" id="passed">-</div>
    </div>
    <div class="card">
        Failed
        <div class="value" id="failed">-</div>
    </div>
    <div class="card">
        Errors
        <div class="value" id="errors">-</div>
    </div>
    <div class="card">
        Pass Rate
        <div class="value" id="pass-rate">-</div>
    </div>
    <div class="card">
        Avg Duration
        <div class="value" id="avg-duration">-</div>
    </div>
</div>

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

<script>
async function loadDashboard() {
    const report = await fetch(
        "/api/executions/report"
    ).then(r => r.json());

    document.getElementById("total").textContent =
        report.total_executions;

    document.getElementById("passed").textContent =
        report.passed;

    document.getElementById("failed").textContent =
        report.failed;

    document.getElementById("errors").textContent =
        report.error;

    document.getElementById("pass-rate").textContent =
        report.pass_rate_percent.toFixed(1) + "%";

    document.getElementById("avg-duration").textContent =
        report.average_duration_seconds.toFixed(2) + "s";

    const executions = await fetch(
        "/api/executions?limit=20"
    ).then(r => r.json());

    const executionBody =
        document.getElementById(
            "executions-body"
        );

    executionBody.innerHTML = executions.map(
        item => `
<tr>
<td>${item.execution_id}</td>
<td>${item.automation_case_id}</td>
<td class="status-${item.status}">
${item.status}
</td>
<td>${Number(
    item.duration_seconds
).toFixed(2)}s</td>
</tr>`
    ).join("");

    const failures = await fetch(
        "/api/executions/failures?limit=20"
    ).then(r => r.json());

    const failureBody =
        document.getElementById(
            "failures-body"
        );

    failureBody.innerHTML = failures.failures.map(
        item => `
<tr>
<td>${item.execution_id}</td>
<td>${item.automation_case_id}</td>
<td class="status-${item.status}">
${item.status}
</td>
<td>${item.message}</td>
</tr>`
    ).join("");
}

loadDashboard();
</script>

</body>
</html>
        """
    )
