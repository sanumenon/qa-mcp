function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function loadQAProjects(selectedProjectId = "") {

    const select =
        document.getElementById("qa-project-id");

    try {

        const response =
            await fetch("/api/projects");

        const payload =
            await response.json();

        if (!response.ok) {
            throw new Error(
                payload.detail ||
                "Unable to load QA projects."
            );
        }

        select.innerHTML =
            '<option value="">Select a project</option>';

        payload.forEach(project => {

            const option =
                document.createElement("option");

            option.value =
                project.project_id;

            option.textContent =
                `${project.name} — ${project.project_id}`;

            select.appendChild(option);
        });

        if (selectedProjectId) {
            select.value = selectedProjectId;
        }

        if (
            !select.value &&
            payload.length === 1
        ) {
            select.value =
                payload[0].project_id;
        }

        updateSelectedProjectId();

    } catch (error) {

        console.error(
            "Project loading failed:",
            error
        );

        select.innerHTML =
            '<option value="">Unable to load projects</option>';
    }
}

function updateSelectedProjectId() {

    const select =
        document.getElementById(
            "qa-project-id"
        );

    const selectedProjectId =
        select.value;

    const display =
        document.getElementById(
            "selected-project-id"
        );

    if (selectedProjectId) {
        display.textContent =
            "Selected Project ID: " +
            selectedProjectId;
    } else {
        display.textContent = "";
    }
}

async function createQAProject() {

    const projectId =
        document
            .getElementById("project-id")
            .value
            .trim();

    const name =
        document
            .getElementById("project-name")
            .value
            .trim();

    const application =
        document
            .getElementById(
                "project-application"
            )
            .value
            .trim();

    const environment =
        document
            .getElementById(
                "project-environment"
            )
            .value
            .trim();

    const description =
        document
            .getElementById(
                "project-description"
            )
            .value
            .trim();

    const errorElement =
        document.getElementById(
            "project-error"
        );

    const successElement =
        document.getElementById(
            "project-success"
        );

    errorElement.textContent = "";
    successElement.textContent = "";

    if (!projectId) {
        errorElement.textContent =
            "Project ID is required.";
        return;
    }

    if (!name) {
        errorElement.textContent =
            "Project name is required.";
        return;
    }

    if (!application) {
        errorElement.textContent =
            "Application is required.";
        return;
    }

    if (!environment) {
        errorElement.textContent =
            "Environment is required.";
        return;
    }

    try {

        const response = await fetch(
            "/api/projects",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    project_id: projectId,
                    name: name,
                    application: application,
                    environment: environment,
                    description: description
                })
            }
        );

        const payload =
            await response.json();

        if (!response.ok) {
            throw new Error(
                payload.detail ||
                "Unable to create QA project."
            );
        }

        await loadQAProjects(
            payload.project_id
        );

        successElement.textContent =
            "QA project created successfully: " +
            payload.project_id;

    } catch (error) {

        errorElement.textContent =
            error.message;
    }
}


async function generateQASuite() {

    const projectId =
        document
            .getElementById(
                "qa-project-id"
            )
            .value
            .trim();

    const requirement =
        document
            .getElementById(
                "qa-requirement"
            )
            .value
            .trim();

    const errorElement =
        document.getElementById(
            "qa-workspace-error"
        );

    const resultElement =
        document.getElementById(
            "qa-workspace-result"
        );

    errorElement.textContent = "";
    resultElement.innerHTML = "";

    if (!projectId) {
        errorElement.textContent =
            "Project ID is required.";
        return;
    }

    if (!requirement) {
        errorElement.textContent =
            "Requirement is required.";
        return;
    }

    try {

        const response = await fetch(
            "/api/projects/" +
            encodeURIComponent(projectId) +
            "/qa-suite",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    requirement: requirement
                })
            }
        );

        const payload =
            await response.json();

        if (!response.ok) {
            throw new Error(
                payload.detail ||
                "Unable to generate QA suite."
            );
        }

        renderQASuite(payload);

    } catch (error) {

        errorElement.textContent =
            error.message;
    }
}


function renderQASuite(payload) {

    const resultElement =
        document.getElementById(
            "qa-workspace-result"
        );

    const analysis =
        payload.analysis;

    const testCases =
        payload.test_cases.test_cases;

    const review =
        payload.review;


    const testCaseRows =
        testCases.map(
            item => `
<tr>
<td>${escapeHtml(item.id)}</td>
<td>${escapeHtml(item.title)}</td>
<td>${escapeHtml(item.priority)}</td>
<td>${escapeHtml(item.test_type)}</td>
<td>
${escapeHtml(item.expected_result)}
</td>
</tr>
`
        ).join("");


    resultElement.innerHTML = `

<h3>QA Suite Generated Successfully</h3>

<div class="grid">

    <div class="card">
        Project
        <div class="value">
            ${escapeHtml(
                payload.project.name
            )}
        </div>
    </div>


    <div class="card">
        Requirement Version
        <div class="value">
            ${escapeHtml(
                String(
                    payload
                        .requirement_version
                        .version
                )
            )}
        </div>
    </div>


    <div class="card">
        Suite Version
        <div class="value">
            ${escapeHtml(
                String(
                    payload
                        .suite_version
                        .version
                )
            )}
        </div>
    </div>


    <div class="card">
        Coverage Score
        <div class="value">
            ${escapeHtml(
                String(
                    review.coverage_score
                )
            )}%
        </div>
    </div>

</div>


<section class="result-block">

<h3>Requirement Analysis</h3>

<p>
<strong>Summary:</strong>
${escapeHtml(analysis.summary)}
</p>


<h4>Actors</h4>

<ul>
${analysis.actors.map(
    item =>
        `<li>${escapeHtml(item)}</li>`
).join("")}
</ul>


<h4>Functional Requirements</h4>

<ul>
${analysis.functional_requirements.map(
    item =>
        `<li>${escapeHtml(item)}</li>`
).join("")}
</ul>


<h4>Positive Scenarios</h4>

<ul>
${analysis.positive_scenarios.map(
    item =>
        `<li>${escapeHtml(item)}</li>`
).join("")}
</ul>


<h4>Negative Scenarios</h4>

<ul>
${analysis.negative_scenarios.map(
    item =>
        `<li>${escapeHtml(item)}</li>`
).join("")}
</ul>


<h4>Edge Cases</h4>

<ul>
${analysis.edge_cases.map(
    item =>
        `<li>${escapeHtml(item)}</li>`
).join("")}
</ul>

</section>


<section class="result-block">

<h3>Generated Test Cases</h3>

<table>

<thead>

<tr>
<th>ID</th>
<th>Title</th>
<th>Priority</th>
<th>Type</th>
<th>Expected Result</th>
</tr>

</thead>

<tbody>
${testCaseRows}
</tbody>

</table>

</section>


<section class="result-block">

<h3>AI Review</h3>

<p>
<strong>Quality:</strong>
${escapeHtml(review.overall_quality)}
</p>

<p>
<strong>Coverage:</strong>
${escapeHtml(
    String(review.coverage_score)
)}%
</p>

<p>
<strong>Summary:</strong>
${escapeHtml(review.summary)}
</p>


<h4>Recommendations</h4>

<ul>
${review.recommendations.map(
    item =>
        `<li>${escapeHtml(item)}</li>`
).join("")}
</ul>


<h4>Missing Scenarios</h4>

<ul>
${review.missing_scenarios.map(
    item =>
        `<li>${escapeHtml(item)}</li>`
).join("")}
</ul>

</section>

`;
}


async function loadDashboard() {

    await loadQAProjects();

    try {

        const report =
            await fetch(
                "/api/executions/report"
            ).then(
                response =>
                    response.json()
            );

        document.getElementById(
            "total"
        ).textContent =
            report.total_executions;

        document.getElementById(
            "passed"
        ).textContent =
            report.passed;

        document.getElementById(
            "failed"
        ).textContent =
            report.failed;

        document.getElementById(
            "errors"
        ).textContent =
            report.error;

        document.getElementById(
            "pass-rate"
        ).textContent =
            report.pass_rate_percent
                .toFixed(1) +
            "%";

        document.getElementById(
            "avg-duration"
        ).textContent =
            report
                .average_duration_seconds
                .toFixed(2) +
            "s";


        const executions =
            await fetch(
                "/api/executions?limit=20"
            ).then(
                response =>
                    response.json()
            );


        const executionBody =
            document.getElementById(
                "executions-body"
            );


        executionBody.innerHTML =
            executions.map(
                item => `
<tr>
<td>
${escapeHtml(item.execution_id)}
</td>
<td>
${escapeHtml(
    item.automation_case_id
)}
</td>
<td class="status-${escapeHtml(
    item.status
)}">
${escapeHtml(item.status)}
</td>
<td>
${Number(
    item.duration_seconds
).toFixed(2)}s
</td>
</tr>
`
            ).join("");


        const failures =
            await fetch(
                "/api/executions/failures?limit=20"
            ).then(
                response =>
                    response.json()
            );


        const failureBody =
            document.getElementById(
                "failures-body"
            );


        failureBody.innerHTML =
            failures.failures.map(
                item => `
<tr>
<td>
${escapeHtml(item.execution_id)}
</td>
<td>
${escapeHtml(
    item.automation_case_id
)}
</td>
<td class="status-${escapeHtml(
    item.status
)}">
${escapeHtml(item.status)}
</td>
<td>
${escapeHtml(item.message)}
</td>
</tr>
`
            ).join("");

    } catch (error) {

        console.error(
            "Dashboard loading failed:",
            error
        );
    }
}


async function initializeDashboard() {
    await loadQAProjects();
    await loadDashboard();
}

initializeDashboard();
