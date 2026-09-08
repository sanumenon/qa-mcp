function escapeHtml(value) {

    const element =
        document.createElement("div");

    element.textContent =
        value == null ? "" : String(value);

    return element.innerHTML;
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
        document
            .getElementById(
                "repository-project-id"
            )
            .value
            .trim();

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

    errorElement.textContent = "";
    resultElement.innerHTML = "";

    if (!projectId) {

        errorElement.textContent =
            "Project ID is required.";

        return;
    }

    button.disabled = true;

    button.textContent =
        "Loading Project Workspace...";

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
            payload
        );

    } catch (error) {

        errorElement.textContent =
            error.message ||
            "Unable to load project workspace.";

    } finally {

        button.disabled = false;

        button.textContent =
            "Load Project Workspace";
    }
}


function renderProjectQAWorkspace(
    payload
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
            item => `
<tr>
<td>${escapeHtml(item.id || "")}</td>
<td>${escapeHtml(item.title || "")}</td>
<td>${escapeHtml(item.priority || "")}</td>
<td>${escapeHtml(item.test_type || "")}</td>
<td>${item.automation_candidate ? "Yes" : "No"}</td>
<td>${escapeHtml(String(item.suite_version || ""))}</td>
</tr>
`
        ).join("");

    const artifactRows =
        automationArtifacts.map(
            item => `
<tr>
<td>${escapeHtml(item.artifact_id || "")}</td>
<td>${escapeHtml(item.test_case_id || "")}</td>
<td>${escapeHtml(item.automation_case_id || "")}</td>
<td>${escapeHtml(item.framework || "")}</td>
<td>${escapeHtml(item.language || "")}</td>
</tr>
`
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
</tr>
</thead>

<tbody>
${artifactRows}
</tbody>

</table>

`;
}


document.addEventListener(
    "DOMContentLoaded",
    loadProjectQAProjects
);