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

    const testCases =
        payload.test_cases || [];

    const automationArtifacts =
        payload.automation_artifacts || [];

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

`;

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
