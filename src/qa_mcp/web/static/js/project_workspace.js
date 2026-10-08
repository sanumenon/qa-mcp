function escapeHtml(value) {

    const element =
        document.createElement("div");

    element.textContent =
        value == null ? "" : String(value);

    return element.innerHTML;
}


function getProjectId() {

    return document
        .getElementById(
            "repository-project-id"
        )
        .value
        .trim();
}


function getProjectWorkspaceActionButton() {

    return document.getElementById(
        "generate-project-automation-button"
    );
}


function getSelectedAutomationCandidateIds() {

    return Array.from(
        document.querySelectorAll(
            'input[data-automation-candidate="true"]:checked'
        )
    ).map(
        checkbox => checkbox.value
    );
}


function updateProjectAutomationButton() {

    const button =
        getProjectWorkspaceActionButton();

    if (!button) {
        return;
    }

    const selectedIds =
        getSelectedAutomationCandidateIds();

    button.disabled =
        selectedIds.length === 0;

    if (selectedIds.length === 0) {

        button.textContent =
            "Generate Automation for Selected Candidates";

    } else {

        button.textContent =
            `Generate Automation (${selectedIds.length} Selected)`;
    }
}


async function loadProjectQAProjects() {

    const select =
        document.getElementById(
            "repository-project-id"
        );

    try {

        const response =
            await fetch("/api/projects");

        const payload =
            await response.json();

        if (!response.ok) {
            throw new Error(
                "Unable to load projects."
            );
        }

        select.innerHTML =
            '<option value="">Select a project</option>';

        payload.forEach(project => {

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                project.project_id;

            option.textContent =
                `${project.name} — ${project.project_id}`;

            select.appendChild(option);

        });

    } catch (error) {

        document.getElementById(
            "project-workspace-error"
        ).textContent =
            error.message ||
            "Unable to load projects.";

    }
}


async function loadProjectQAWorkspace() {

    const projectId =
        getProjectId();

    const errorElement =
        document.getElementById(
            "project-workspace-error"
        );

    const resultElement =
        document.getElementById(
            "project-workspace-result"
        );

    const button =
        document.getElementById(
            "load-project-workspace-button"
        );

    const automationButton =
        getProjectWorkspaceActionButton();

    errorElement.textContent = "";
    resultElement.innerHTML = "";

    if (!projectId) {

        errorElement.textContent =
            "Project ID is required.";

        if (automationButton) {
            automationButton.disabled = true;
        }

        return;
    }

    button.disabled = true;

    button.textContent =
        "Loading Project Workspace...";

    if (automationButton) {
        automationButton.disabled = true;
    }

    try {

        const response =
            await fetch(
                "/api/projects/" +
                encodeURIComponent(projectId) +
                "/workspace"
            );

        const payload =
            await response.json();

        if (!response.ok) {

            throw new Error(
                payload.detail ||
                "Unable to load project workspace."
            );
        }

        renderProjectQAWorkspace(
            payload,
            projectId
        );

        await loadProjectExecutionHistory();
        await loadProjectExecutionInsights(projectId);

    } catch (error) {

        errorElement.textContent =
            error.message ||
            "Unable to load project workspace.";

    } finally {

        button.disabled = false;

        button.textContent =
            "Load Project Workspace";

        updateProjectAutomationButton();
    }
}


async function generateProjectAutomation() {

    const projectId =
        getProjectId();

    const selectedTestCaseIds =
        getSelectedAutomationCandidateIds();

    const errorElement =
        document.getElementById(
            "project-workspace-error"
        );

    const automationButton =
        getProjectWorkspaceActionButton();

    errorElement.textContent = "";

    if (!projectId) {

        errorElement.textContent =
            "Project ID is required.";

        return;
    }

    if (selectedTestCaseIds.length === 0) {

        errorElement.textContent =
            "Select at least one automation candidate.";

        updateProjectAutomationButton();

        return;
    }

    automationButton.disabled = true;

    automationButton.textContent =
        "Generating Automation...";

    try {

        const response =
            await fetch(
                "/api/projects/" +
                encodeURIComponent(projectId) +
                "/automation",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json",
                    },
                    body: JSON.stringify({
                        selected_test_case_ids:
                            selectedTestCaseIds,
                    }),
                }
            );

        const payload =
            await response.json();

        if (!response.ok) {

            throw new Error(
                payload.detail ||
                "Unable to generate automation."
            );
        }

        renderProjectAutomationResult(
            payload
        );

        await loadProjectQAWorkspace();

    } catch (error) {

        errorElement.textContent =
            error.message ||
            "Unable to generate automation.";

    } finally {

        updateProjectAutomationButton();
    }
}


function renderProjectAutomationResult(
    payload
) {

    const resultElement =
        document.getElementById(
            "project-workspace-result"
        );

    const automationCases =
        payload.automation_cases || [];

    const automationArtifacts =
        payload.automation_artifacts || [];

    const project =
        payload.project || {};

    const summary =
        document.createElement("div");

    summary.className =
        "result-block";

    summary.innerHTML = `
<h4>Automation Generation Result</h4>
<p>
Project:
<strong>
${escapeHtml(
    project.name ||
    project.project_id ||
    ""
)}
</strong>
</p>
<p>
Selected test cases:
${escapeHtml(
    String(
        (payload.selected_test_case_ids || []).length
    )
)}
</p>
<p>
Automation cases generated:
${escapeHtml(
    String(automationCases.length)
)}
</p>
<p>
Automation artifacts generated:
${escapeHtml(
    String(automationArtifacts.length)
)}
</p>
`;

    resultElement.prepend(
        summary
    );
}


async function executeProjectAutomation(
    artifactId
) {

    const projectId =
        getProjectId();

    const errorElement =
        document.getElementById(
            "project-workspace-error"
        );

    const resultElement =
        document.getElementById(
            "project-workspace-result"
        );

    if (!projectId || !artifactId) {

        errorElement.textContent =
            "Project ID and artifact ID are required.";

        return;
    }

    errorElement.textContent = "";

    try {

        const response =
            await fetch(
                "/api/projects/" +
                encodeURIComponent(projectId) +
                "/automation/" +
                encodeURIComponent(artifactId) +
                "/execute",
                {
                    method: "POST"
                }
            );

        const payload =
            await response.json();

        if (!response.ok) {

            throw new Error(
                payload.detail ||
                "Unable to execute automation."
            );
        }

        const status =
            escapeHtml(payload.status || "");

        const stdout =
            escapeHtml(
                payload.stdout ||
                payload.output ||
                ""
            );

        const stderr =
            escapeHtml(
                payload.stderr ||
                payload.error ||
                ""
            );

        resultElement.insertAdjacentHTML(
            "afterbegin",
            `
        <p>
        <strong>Execution result for
        ${escapeHtml(artifactId)}:
        ${status}
        </strong>
        </p>

        ${
            stdout
                ? `
        <h5>Output</h5>
        <pre>${stdout}</pre>
        `
                : ""
        }

        ${
            stderr
                ? `
        <h5>Error Output</h5>
        <pre>${stderr}</pre>
        `
                : ""
        }
        `
        );

        await loadProjectExecutionHistory();
        await loadProjectExecutionInsights(projectId);

    } catch (error) {

        errorElement.textContent =
            error.message ||
            "Unable to execute automation.";

    }
}


function renderProjectQAWorkspace(
    payload,
    projectId
) {

    const resultElement =
        document.getElementById(
            "project-workspace-result"
        );

    const requirements =
        payload.requirement_versions || [];

    const suiteVersions =
        payload.suite_versions || [];

    const testCasesPayload =
        payload.test_cases || [];

    const testCases =
        Array.isArray(testCasesPayload)
            ? testCasesPayload
            : testCasesPayload.test_cases || [];

    const automationArtifacts =
        payload.automation_artifacts || [];

    const testCasesById = new Map(
        testCases.map(item => [String(item.id || ""), item])
    );

    const requirementRows =
        requirements.map(
            item => `
<tr>
<td>${escapeHtml(item.version_id || "")}</td>
<td>${escapeHtml(String(item.version || ""))}</td>
<td>${escapeHtml(item.requirement || "")}</td>
</tr>
`
        ).join("");

    const suiteRows =
        suiteVersions.map(
            item => `
<tr>
<td>${escapeHtml(item.suite_id || "")}</td>
<td>${escapeHtml(String(item.version || ""))}</td>
<td>${escapeHtml(item.requirement_version_id || "")}</td>
</tr>
`
        ).join("");

    const testCaseRows =
        testCases.map(
            item => {

                const isCandidate =
                    item.automation_candidate === true;

                const checkbox =
                    isCandidate
                        ? `
<input
    type="checkbox"
    value="${escapeHtml(item.id || "")}"
    data-automation-candidate="true"
    aria-label="Select ${escapeHtml(item.title || item.id || "")}"
    onchange="updateProjectAutomationButton()"
>
`
                        : "";

                return `
<tr>
<td>${checkbox}</td>
<td>${escapeHtml(item.id || "")}</td>
<td>${escapeHtml(item.title || "")}</td>
<td>${escapeHtml(item.priority || "")}</td>
<td>${escapeHtml(item.test_type || "")}</td>
<td>${isCandidate ? "Yes" : "No"}</td>
<td>${escapeHtml(String(item.suite_version || ""))}</td>
</tr>
`;
            }
        ).join("");

    const artifactRows =
        automationArtifacts.map(
            item => {

                const artifactId =
                    item.artifact_id || "";

                return `
<tr>
<td>${escapeHtml(artifactId)}</td>
<td>${escapeHtml(item.test_case_id || "")}</td>
<td>${escapeHtml(item.automation_case_id || "")}</td>
<td>${escapeHtml(item.framework || "")}</td>
<td>${escapeHtml(item.language || "")}</td>
<td>
<button
    type="button"
    data-review-artifact="${escapeHtml(artifactId)}"
>
    Review
</button>
<button
    type="button"
    onclick="executeProjectAutomation('${escapeHtml(artifactId)}')"
>
    Execute
</button>
</td>
</tr>
`;
            }
        ).join("");

    const project =
        payload.project || {};

    resultElement.innerHTML = `

<h3>
${escapeHtml(
    project.name ||
    project.project_id
)}
</h3>

<h4>Requirement Versions</h4>

<table>

<thead>
<tr>
<th>Version ID</th>
<th>Version</th>
<th>Requirement</th>
</tr>
</thead>

<tbody>
${requirementRows}
</tbody>

</table>


<h4>Saved Suite Versions</h4>

<table>

<thead>
<tr>
<th>Suite ID</th>
<th>Version</th>
<th>Requirement Version</th>
</tr>
</thead>

<tbody>
${suiteRows}
</tbody>

</table>


<h4>Saved Test Cases</h4>

<table>

<thead>
<tr>
<th>Select</th>
<th>ID</th>
<th>Title</th>
<th>Priority</th>
<th>Type</th>
<th>Automation Candidate</th>
<th>Suite Version</th>
</tr>
</thead>

<tbody>
${testCaseRows}
</tbody>

</table>


<h4>Generated Automation Artifacts</h4>

<table>

<thead>
<tr>
<th>Artifact ID</th>
<th>Test Case</th>
<th>Automation Case</th>
<th>Framework</th>
<th>Language</th>
<th>Actions</th>
</tr>
</thead>

<tbody>
${artifactRows}
</tbody>

</table>

<section
    id="project-artifact-review"
    class="artifact-review"
    aria-live="polite"
    hidden
></section>

`;

    const reviewElement = document.getElementById(
        "project-artifact-review"
    );

    const setReviewText = (label, value) => {
        const row = document.createElement("p");
        const heading = document.createElement("strong");
        heading.textContent = `${label}: `;
        row.appendChild(heading);
        row.appendChild(
            document.createTextNode(
                value == null ? "" : String(value)
            )
        );
        reviewElement.appendChild(row);
    };

    resultElement
        .querySelectorAll("[data-review-artifact]")
        .forEach(button => {
            button.addEventListener("click", () => {
                const artifact = automationArtifacts.find(
                    item =>
                        String(item.artifact_id || "") ===
                        button.dataset.reviewArtifact
                );

                if (!artifact || !reviewElement) {
                    return;
                }

                reviewElement.replaceChildren();
                reviewElement.hidden = false;

                const heading = document.createElement("h4");
                heading.textContent = "Generated Artifact Review";
                reviewElement.appendChild(heading);

                const closeButton = document.createElement("button");
                closeButton.type = "button";
                closeButton.textContent = "Close Review";
                closeButton.addEventListener("click", () => {
                    reviewElement.hidden = true;
                    reviewElement.replaceChildren();
                });
                reviewElement.appendChild(closeButton);

                setReviewText("Artifact ID", artifact.artifact_id);
                setReviewText("Filename", artifact.file_name);
                setReviewText("Framework", artifact.framework);
                setReviewText("Language", artifact.language);
                if (artifact.created_at) {
                    setReviewText(
                        "Created",
                        formatExecutionDate(artifact.created_at)
                    );
                }
                setReviewText(
                    "Project",
                    project.name || project.project_id || projectId
                );

                const testCase = testCasesById.get(
                    String(artifact.test_case_id || "")
                );
                setReviewText(
                    "Test Case",
                    testCase
                        ? `${testCase.id || artifact.test_case_id}${
                            testCase.title ? ` — ${testCase.title}` : ""
                        }`
                        : artifact.test_case_id
                );
                setReviewText(
                    "Automation Case",
                    artifact.automation_case_id
                );

                const sourceHeading = document.createElement("h5");
                sourceHeading.textContent = "Generated Source";
                reviewElement.appendChild(sourceHeading);

                const source = document.createElement("pre");
                source.className = "artifact-review-source";
                source.setAttribute(
                    "aria-label",
                    "Generated artifact source code"
                );
                source.textContent =
                    artifact.code == null ? "" : String(artifact.code);
                reviewElement.appendChild(source);
            });
        });

    updateProjectAutomationButton();
}

function formatExecutionDate(value) {
    if (!value) {
        return "";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return date.toLocaleString();
}


function executionStatusClass(status) {
    const normalized = String(status || "").toLowerCase();

    if (
        normalized === "passed" ||
        normalized === "success" ||
        normalized === "completed"
    ) {
        return "execution-status-passed";
    }

    if (
        normalized === "failed" ||
        normalized === "error"
    ) {
        return "execution-status-failed";
    }

    return "execution-status-other";
}


function renderProjectExecutionReview(payload) {
    const reviewElement = document.getElementById(
        "project-execution-review"
    );

    if (!reviewElement) {
        return;
    }

    const execution = payload || {};
    const artifact = execution.artifact || {};
    const project = execution.project || {};

    const executionId =
        execution.execution_id ||
        execution.id ||
        "";

    const status =
        execution.status ||
        "Unknown";

    const stdout =
        execution.stdout ||
        execution.output ||
        "";

    const stderr =
        execution.stderr ||
        execution.error ||
        "";

    const error =
        execution.error ||
        "";

    reviewElement.innerHTML = `
<h4>Execution Review</h4>

<p>
<strong>Execution ID:</strong>
${escapeHtml(executionId)}
</p>

<p>
<strong>Project:</strong>
${escapeHtml(
    project.name ||
    project.project_id ||
    getProjectId()
)}
</p>

<p>
<strong>Status:</strong>
<span class="${executionStatusClass(status)}">
${escapeHtml(status)}
</span>
</p>

<p>
<strong>Automation Artifact:</strong>
${escapeHtml(
    execution.automation_artifact_id ||
    artifact.artifact_id ||
    ""
)}
</p>

<p>
<strong>Automation Case:</strong>
${escapeHtml(
    execution.automation_case_id ||
    artifact.automation_case_id ||
    ""
)}
</p>

<p>
<strong>Exit Code:</strong>
${escapeHtml(
    execution.exit_code == null
        ? ""
        : String(execution.exit_code)
)}
</p>

<p>
<strong>Duration:</strong>
${escapeHtml(
    execution.duration_seconds == null
        ? ""
        : `${execution.duration_seconds} seconds`
)}
</p>

${
    stdout
        ? `
<h5>Standard Output</h5>
<pre>${escapeHtml(stdout)}</pre>
`
        : ""
}

${
    stderr
        ? `
<h5>Standard Error</h5>
<pre>${escapeHtml(stderr)}</pre>
`
        : ""
}

${
    error && error !== stderr
        ? `
<h5>Execution Error</h5>
<pre>${escapeHtml(error)}</pre>
`
        : ""
}
`;
}


async function openProjectExecutionReview(executionId) {
    const projectId = getProjectId();

    const errorElement = document.getElementById(
        "project-workspace-error"
    );

    const reviewElement = document.getElementById(
        "project-execution-review"
    );

    if (!projectId || !executionId) {
        if (errorElement) {
            errorElement.textContent =
                "Project ID and execution ID are required.";
        }

        return;
    }

    if (reviewElement) {
        reviewElement.innerHTML =
            "<p>Loading execution review...</p>";
    }

    if (errorElement) {
        errorElement.textContent = "";
    }

    try {
        const response = await fetch(
            "/api/projects/" +
            encodeURIComponent(projectId) +
            "/executions/" +
            encodeURIComponent(executionId)
        );

        const payload = await response.json();

        if (!response.ok) {
            throw new Error(
                payload.detail ||
                "Unable to load execution review."
            );
        }

        renderProjectExecutionReview(payload);
    } catch (error) {
        if (errorElement) {
            errorElement.textContent =
                error.message ||
                "Unable to load execution review.";
        }

        if (reviewElement) {
            reviewElement.innerHTML = "";
        }
    }
}


function renderProjectExecutionHistory(payload) {
    const historyElement = document.getElementById(
        "project-execution-history"
    );

    if (!historyElement) {
        return;
    }

    const executions = Array.isArray(payload)
        ? payload
        : payload.executions || [];

    if (executions.length === 0) {
        historyElement.innerHTML = `
<h4>Execution History</h4>
<p>No executions have been recorded for this project.</p>
`;

        return;
    }

    const rows = executions.map(execution => {
        const executionId =
            execution.execution_id ||
            execution.id ||
            "";

        const status =
            execution.status ||
            "Unknown";

        const createdAt =
            execution.created_at ||
            execution.started_at ||
            execution.completed_at ||
            "";

        const artifactId =
            execution.automation_artifact_id ||
            "";

        const exitCode =
            execution.exit_code == null
                ? ""
                : String(execution.exit_code);

        return `
<tr>
<td>${escapeHtml(executionId)}</td>
<td>
<span class="${executionStatusClass(status)}">
${escapeHtml(status)}
</span>
</td>
<td>${escapeHtml(artifactId)}</td>
<td>${escapeHtml(exitCode)}</td>
<td>${escapeHtml(formatExecutionDate(createdAt))}</td>
<td>
<button
    type="button"
    onclick="openProjectExecutionReview('${escapeHtml(executionId)}')"
>
    Review
</button>
</td>
</tr>
`;
    }).join("");

    historyElement.innerHTML = `
<h4>Execution History</h4>

<table>
<thead>
<tr>
<th>Execution ID</th>
<th>Status</th>
<th>Artifact</th>
<th>Exit Code</th>
<th>Date</th>
<th>Actions</th>
</tr>
</thead>

<tbody>
${rows}
</tbody>
</table>
`;
}


function renderProjectExecutionInsightsLoading(projectId) {
    const insightsElement = document.getElementById(
        "project-execution-insights"
    );

    if (!insightsElement) {
        return;
    }

    insightsElement.innerHTML = `
<h3>Project Execution Insights</h3>
<p role="status">
Loading execution insights for
${escapeHtml(projectId)}...
</p>
`;
}


function renderProjectExecutionInsightsError(message) {
    const insightsElement = document.getElementById(
        "project-execution-insights"
    );

    if (!insightsElement) {
        return;
    }

    insightsElement.innerHTML = `
<h3>Project Execution Insights</h3>
<p class="error" role="alert">
${escapeHtml(message)}
</p>
`;
}


function renderProjectExecutionInsights(report, analysis) {
    const insightsElement = document.getElementById(
        "project-execution-insights"
    );

    if (!insightsElement) {
        return;
    }

    const totalExecutions = Number(
        report.total_executions || 0
    );
    const passed = Number(report.passed || 0);
    const failed = Number(report.failed || 0);
    const errors = Number(report.error || 0);
    const passRate = Number(
        report.pass_rate_percent || 0
    ).toFixed(1);
    const failures = Array.isArray(analysis.failures)
        ? analysis.failures
        : [];

    const failureRows = failures.map(failure => {
        const executionId = failure.execution_id || "";
        const status = failure.status || "Unknown";

        return `
<tr>
<td>${escapeHtml(executionId)}</td>
<td>
<span class="${executionStatusClass(status)}">
${escapeHtml(status)}
</span>
</td>
<td>${escapeHtml(failure.automation_case_id || "")}</td>
<td class="project-execution-failure-message">
${escapeHtml(failure.message || "Automation execution failed")}
</td>
<td>
<button
    type="button"
    onclick="openProjectExecutionReview('${escapeHtml(executionId)}')"
>
    Review
</button>
</td>
</tr>
`;
    }).join("");

    const executionState = totalExecutions === 0
        ? `
<p class="execution-insight-empty" role="status">
No executions have been recorded for this project yet.
</p>
`
        : "";

    let failureState;

    if (Number(analysis.total_failures || 0) === 0) {
        failureState = `
<p class="execution-insight-healthy" role="status">
No failures recorded for this project.
</p>
`;
    } else if (failures.length === 0) {
        failureState = `
<p class="execution-insight-empty" role="status">
Failures are recorded, but no recent failure details were returned.
</p>
`;
    } else {
        failureState = `
<table>
<thead>
<tr>
<th>Execution</th>
<th>Status</th>
<th>Automation Case</th>
<th>Failure</th>
<th>Actions</th>
</tr>
</thead>
<tbody>
${failureRows}
</tbody>
</table>
`;
    }

    insightsElement.innerHTML = `
<h3>Project Execution Insights</h3>
<div class="execution-insight-grid">
    <div class="execution-insight-card">
        Total Executions
        <strong id="project-insights-total">
            ${escapeHtml(totalExecutions)}
        </strong>
    </div>
    <div class="execution-insight-card">
        Passed
        <strong id="project-insights-passed">
            ${escapeHtml(passed)}
        </strong>
    </div>
    <div class="execution-insight-card">
        Failed
        <strong id="project-insights-failed">
            ${escapeHtml(failed)}
        </strong>
    </div>
    <div class="execution-insight-card">
        Errors
        <strong id="project-insights-errors">
            ${escapeHtml(errors)}
        </strong>
    </div>
    <div class="execution-insight-card">
        Pass Rate
        <strong id="project-insights-pass-rate">
            ${escapeHtml(passRate)}%
        </strong>
    </div>
</div>
${executionState}
<h4>Recent Project Failures</h4>
${failureState}
`;
}


async function loadProjectExecutionInsights(projectId) {
    const insightsElement = document.getElementById(
        "project-execution-insights"
    );

    if (!insightsElement) {
        return;
    }

    if (!projectId) {
        renderProjectExecutionInsightsError(
            "Select a project to view project-scoped execution insights."
        );
        return;
    }

    renderProjectExecutionInsightsLoading(projectId);

    const projectPath =
        "/api/projects/" +
        encodeURIComponent(projectId) +
        "/executions";

    try {
        const [reportResponse, failuresResponse] =
            await Promise.all([
                fetch(projectPath + "/report"),
                fetch(projectPath + "/failures?limit=10"),
            ]);

        const [report, analysis] = await Promise.all([
            reportResponse.json(),
            failuresResponse.json(),
        ]);

        if (!reportResponse.ok) {
            throw new Error(
                report.detail ||
                "Unable to load project execution metrics."
            );
        }

        if (!failuresResponse.ok) {
            throw new Error(
                analysis.detail ||
                "Unable to load project failure analysis."
            );
        }

        renderProjectExecutionInsights(
            report,
            analysis
        );
    } catch (error) {
        renderProjectExecutionInsightsError(
            error.message ||
            "Unable to load project execution insights."
        );
    }
}


async function loadProjectExecutionHistory() {
    const projectId = getProjectId();

    const historyElement = document.getElementById(
        "project-execution-history"
    );

    const errorElement = document.getElementById(
        "project-workspace-error"
    );

    if (!projectId) {
        if (historyElement) {
            historyElement.innerHTML = "";
        }

        return;
    }

    if (historyElement) {
        historyElement.innerHTML =
            "<h4>Execution History</h4><p>Loading...</p>";
    }

    try {
        const response = await fetch(
            "/api/projects/" +
            encodeURIComponent(projectId) +
            "/executions?limit=50"
        );

        const payload = await response.json();

        if (!response.ok) {
            throw new Error(
                payload.detail ||
                "Unable to load execution history."
            );
        }

        renderProjectExecutionHistory(payload);
    } catch (error) {
        if (errorElement) {
            errorElement.textContent =
                error.message ||
                "Unable to load execution history.";
        }

        if (historyElement) {
            historyElement.innerHTML = "";
        }
    }
}

document.addEventListener(
    "DOMContentLoaded",
    loadProjectQAProjects
);
