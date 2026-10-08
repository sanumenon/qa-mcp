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


async function selectProjectWorkspace() {
    const projectId = getProjectId();
    const url = new URL(window.location.href);
    if (projectId) {
        url.searchParams.set("project_id", projectId);
    } else {
        url.searchParams.delete("project_id");
    }
    window.history.replaceState(null, "", url);

    if (projectId) {
        await loadProjectQAWorkspace();
    } else {
        const actionContainer = document.getElementById(
            "project-workspace-action"
        );
        const actionMount = document.getElementById(
            "project-workspace-action-mount"
        );
        if (actionContainer && actionMount) {
            actionMount.appendChild(actionContainer);
            actionContainer.hidden = true;
        }
        const automationButton = getProjectWorkspaceActionButton();
        if (automationButton) {
            automationButton.disabled = true;
        }
        document.getElementById(
            "project-workspace-result"
        ).replaceChildren();
        document.querySelectorAll(".project-area-panel").forEach(panel => {
            panel.hidden = true;
        });
        document.getElementById(
            "project-execution-history"
        ).replaceChildren();
        document.getElementById(
            "project-execution-review"
        ).replaceChildren();
        document.getElementById(
            "project-execution-insights"
        ).textContent = "Select a project to view its execution insights.";
    }
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


function setProjectWorkspaceArea(area) {
    const tabs = Array.from(
        document.querySelectorAll("[data-project-area]")
    );

    tabs.forEach(tab => {
        const selected = tab.dataset.projectArea === area;
        tab.setAttribute("aria-selected", String(selected));
        tab.tabIndex = selected ? 0 : -1;
    });

    document.querySelectorAll(".project-area-panel").forEach(panel => {
        panel.hidden = panel.id !== `project-area-${area}`;
    });

    const actionContainer = document.getElementById(
        "project-workspace-action"
    );
    if (actionContainer) {
        actionContainer.hidden = area !== "automation";
    }
}


function updateProjectOverview(report, analysis) {
    const values = {
        "project-overview-execution-count": report.total_executions || 0,
        "project-overview-passed": report.passed || 0,
        "project-overview-failed": report.failed || 0,
        "project-overview-pass-rate":
            `${Number(report.pass_rate_percent || 0).toFixed(1)}%`,
    };
    Object.entries(values).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = String(value);
        }
    });

    const activity = document.getElementById(
        "project-overview-activity"
    );
    if (!activity) {
        return;
    }

    activity.replaceChildren();
    const latestFailure = Array.isArray(analysis.failures)
        ? analysis.failures[0]
        : null;
    const message = document.createElement("p");
    if (latestFailure) {
        message.textContent =
            `Recent failure: ${latestFailure.message || "Execution failed"}`;
        const reviewButton = document.createElement("button");
        reviewButton.type = "button";
        reviewButton.textContent = "Review failure";
        reviewButton.addEventListener("click", () => {
            setProjectWorkspaceArea("executions");
            openProjectExecutionReview(latestFailure.execution_id);
        });
        activity.append(message, reviewButton);
    } else if (Number(report.total_executions || 0) === 0) {
        message.textContent = "No executions have been recorded for this project yet.";
        activity.appendChild(message);
    } else {
        message.textContent = "No recent failures recorded for this project.";
        activity.appendChild(message);
    }
}


function renderProjectOverviewError(message) {
    [
        "project-overview-execution-count",
        "project-overview-passed",
        "project-overview-failed",
        "project-overview-pass-rate",
    ].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = "Unavailable";
        }
    });
    const activity = document.getElementById(
        "project-overview-activity"
    );
    if (activity) {
        activity.textContent = message;
    }
}


function applySavedTestCaseFilters() {
    const search = (
        document.getElementById("saved-test-case-search")?.value || ""
    ).trim().toLowerCase();
    const priority =
        document.getElementById("saved-test-case-priority")?.value || "";
    const testType =
        document.getElementById("saved-test-case-type")?.value || "";
    const candidate =
        document.getElementById("saved-test-case-candidate")?.value || "";
    const rows = Array.from(
        document.querySelectorAll("[data-test-case-filter-row]")
    );

    let visible = 0;
    rows.forEach(row => {
        const matches =
            (!search || row.dataset.search.includes(search)) &&
            (!priority || row.dataset.priority === priority) &&
            (!testType || row.dataset.testType === testType) &&
            (!candidate || row.dataset.automationCandidate === candidate);
        row.hidden = !matches;
        if (matches) {
            visible += 1;
        }
    });

    const count = document.getElementById("saved-test-case-count");
    if (count) {
        count.textContent = `Showing ${visible} of ${rows.length} test cases`;
    }
}


function getGeneratedProjectTestCaseIds() {
    return Array.from(
        document.querySelectorAll(
            "#generated-project-test-cases input[type=checkbox]:checked"
        )
    ).map(checkbox => checkbox.value);
}


function updateGeneratedProjectTestCaseCount() {
    const selected = getGeneratedProjectTestCaseIds().length;
    const total = document.querySelectorAll(
        "#generated-project-test-cases input[type=checkbox]"
    ).length;
    const count = document.getElementById(
        "generated-project-test-case-count"
    );
    if (count) {
        count.textContent = `Selected ${selected} of ${total} test cases`;
    }
}


function selectAllGeneratedProjectTestCases(selected) {
    document.querySelectorAll(
        "#generated-project-test-cases input[type=checkbox]"
    ).forEach(checkbox => {
        checkbox.checked = selected;
    });
    updateGeneratedProjectTestCaseCount();
}


async function generateProjectQASuite(event) {
    event.preventDefault();
    const projectId = getProjectId();
    const requirement = document.getElementById(
        "project-qa-requirement"
    ).value.trim();
    const errorElement = document.getElementById(
        "project-qa-generation-error"
    );
    const resultElement = document.getElementById(
        "project-qa-generation-result"
    );
    const button = document.getElementById(
        "project-qa-generate-button"
    );
    errorElement.textContent = "";
    const noticeElement = document.getElementById(
        "project-workspace-notice"
    );
    if (noticeElement) {
        noticeElement.textContent = "";
    }
    resultElement.replaceChildren();

    if (!projectId || !requirement) {
        errorElement.textContent = !projectId
            ? "Select a project before generating a QA suite."
            : "Requirement is required.";
        return;
    }

    button.disabled = true;
    button.textContent = "Generating QA Suite...";
    try {
        const response = await fetch(
            `/api/projects/${encodeURIComponent(projectId)}/qa-suite`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ requirement }),
            }
        );
        const payload = await response.json();
        if (!response.ok) {
            throw new Error(
                payload.detail || "Unable to generate QA suite."
            );
        }
        window.projectQASuitePayload = payload;
        renderProjectQASuitePreview(payload);
    } catch (error) {
        errorElement.textContent =
            error.message || "Unable to generate QA suite.";
    } finally {
        button.disabled = false;
        button.textContent = "Generate QA Suite";
    }
}


function renderProjectQASuitePreview(payload) {
    const result = document.getElementById(
        "project-qa-generation-result"
    );
    const casesPayload = payload.test_cases || {};
    const testCases = Array.isArray(casesPayload)
        ? casesPayload
        : casesPayload.test_cases || [];
    const analysis = payload.analysis || {};
    const review = payload.review || {};
    const coverage = review.coverage_score == null
        ? ""
        : `${escapeHtml(String(review.coverage_score))}%`;
    const rows = testCases.map((testCase, index) => `
<tr>
    <td><input type="checkbox" checked value="${escapeHtml(testCase.id || "")}" aria-label="Select generated test case ${escapeHtml(testCase.id || "")}" onchange="updateGeneratedProjectTestCaseCount()"></td>
    <td>${escapeHtml(testCase.id || "")}</td>
    <td>${escapeHtml(testCase.title || "")}</td>
    <td>${escapeHtml(testCase.priority || "")}</td>
    <td>${escapeHtml(testCase.test_type || "")}</td>
    <td><button type="button" data-generated-case-review="${index}">Review</button></td>
</tr>
`).join("");

    result.innerHTML = `
<div class="project-qa-generation-summary">
    <h4>Generated QA Suite</h4>
    <p>${escapeHtml(analysis.summary || "Requirement analysis complete.")}</p>
    <p>Coverage review: ${escapeHtml(review.overall_quality || "Available")}${coverage ? ` · ${coverage}` : ""}</p>
</div>
<div class="generated-case-selection" id="generated-project-test-cases">
    <div class="generated-case-actions">
        <button type="button" class="secondary-button" data-select-generated-cases="all">Select All</button>
        <button type="button" class="secondary-button" data-select-generated-cases="none">Clear All</button>
        <span id="generated-project-test-case-count" role="status">Selected ${testCases.length} of ${testCases.length} test cases</span>
    </div>
    <div class="table-scroll"><table>
        <thead><tr><th>Select</th><th>ID</th><th>Title</th><th>Priority</th><th>Type</th><th>Review</th></tr></thead>
        <tbody>${rows || '<tr><td colspan="6">No test cases were generated.</td></tr>'}</tbody>
    </table></div>
    <section id="generated-project-test-case-review" class="test-case-review" aria-live="polite" hidden></section>
    <button type="button" class="primary-button" id="save-generated-project-test-cases">Save Selected Test Cases</button>
    <div id="project-qa-save-error" class="error" role="alert"></div>
</div>
`;

    result.querySelectorAll("[data-select-generated-cases]")
        .forEach(button => {
            button.addEventListener("click", () => {
                selectAllGeneratedProjectTestCases(
                    button.dataset.selectGeneratedCases === "all"
                );
            });
        });
    result.querySelectorAll("[data-generated-case-review]")
        .forEach(button => {
            button.addEventListener("click", () => {
                const testCase = testCases[
                    Number(button.dataset.generatedCaseReview)
                ];
                const panel = document.getElementById(
                    "generated-project-test-case-review"
                );
                if (testCase && panel) {
                    renderProjectTestCaseReview(
                        testCase,
                        panel,
                        "Generated Test Case Review",
                        false
                    );
                }
            });
        });
    document.getElementById(
        "save-generated-project-test-cases"
    ).addEventListener("click", saveGeneratedProjectTestCases);
}


async function saveGeneratedProjectTestCases() {
    const suite = window.projectQASuitePayload;
    const errorElement = document.getElementById("project-qa-save-error");
    const successElement = document.getElementById("project-workspace-notice");
    const selectedIds = getGeneratedProjectTestCaseIds();
    errorElement.textContent = "";
    successElement.textContent = "";
    if (!selectedIds.length) {
        errorElement.textContent = "Select at least one test case to save.";
        return;
    }

    const projectId = getProjectId();
    const requirementVersion = suite.requirement_version || {};
    try {
        const response = await fetch(
            `/api/projects/${encodeURIComponent(projectId)}/qa-suite/save`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    requirement_version_id: requirementVersion.version_id,
                    test_cases: suite.test_cases,
                    review: suite.review,
                    selected_test_case_ids: selectedIds,
                }),
            }
        );
        const payload = await response.json();
        if (!response.ok) {
            throw new Error(payload.detail || "Unable to save test cases.");
        }
        await loadProjectQAWorkspace();
        setProjectWorkspaceArea("test-cases");
        successElement.textContent =
            `Saved ${selectedIds.length} test case${selectedIds.length === 1 ? "" : "s"}.`;
    } catch (error) {
        errorElement.textContent =
            error.message || "Unable to save test cases.";
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

        const requestedProjectId =
            new URLSearchParams(window.location.search)
                .get("project_id");

        if (
            requestedProjectId &&
            payload.some(
                project =>
                    project.project_id === requestedProjectId
            )
        ) {
            select.value = requestedProjectId;
            await loadProjectQAWorkspace();
        }

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
    document.getElementById("project-workspace-notice").textContent = "";
    const actionContainer = document.getElementById(
        "project-workspace-action"
    );
    const actionMount = document.getElementById(
        "project-workspace-action-mount"
    );
    if (actionContainer && actionMount) {
        actionMount.appendChild(actionContainer);
    }
    resultElement.innerHTML = "";
    setProjectWorkspaceArea("overview");

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

        await Promise.all([
            loadProjectExecutionHistory(),
            loadProjectExecutionInsights(projectId),
        ]);

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


function appendTestCaseReviewValue(
    reviewElement,
    label,
    value
) {
    const row = document.createElement("p");
    const heading = document.createElement("strong");
    heading.textContent = `${label}: `;
    row.appendChild(heading);
    row.appendChild(
        document.createTextNode(
            value == null || value === ""
                ? "Not provided"
                : String(value)
        )
    );
    reviewElement.appendChild(row);
}


function appendTestCaseReviewList(
    reviewElement,
    label,
    values,
    ordered = false
) {
    const heading = document.createElement("h5");
    heading.textContent = label;
    reviewElement.appendChild(heading);

    const list = document.createElement(
        ordered ? "ol" : "ul"
    );
    const entries = Array.isArray(values) ? values : [];

    if (entries.length === 0) {
        const emptyItem = document.createElement("li");
        emptyItem.textContent = "None provided";
        list.appendChild(emptyItem);
    } else {
        entries.forEach(value => {
            const item = document.createElement("li");
            item.textContent = value == null ? "" : String(value);
            list.appendChild(item);
        });
    }

    reviewElement.appendChild(list);
}


function renderProjectTestCaseReview(
    testCase,
    reviewElement,
    headingText = "Saved Test Case Review",
    includeVersionMetadata = true
) {
    reviewElement.replaceChildren();
    reviewElement.hidden = false;

    const heading = document.createElement("h4");
    heading.textContent = headingText;
    reviewElement.appendChild(heading);

    const closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.textContent = "Close Review";
    closeButton.addEventListener("click", () => {
        reviewElement.hidden = true;
        reviewElement.replaceChildren();
    });
    reviewElement.appendChild(closeButton);

    appendTestCaseReviewValue(
        reviewElement,
        "Test Case ID",
        testCase.id
    );
    appendTestCaseReviewValue(
        reviewElement,
        "Title",
        testCase.title
    );
    appendTestCaseReviewValue(
        reviewElement,
        "Priority",
        testCase.priority
    );
    appendTestCaseReviewValue(
        reviewElement,
        "Test Type",
        testCase.test_type
    );
    if (includeVersionMetadata) {
        appendTestCaseReviewValue(
            reviewElement,
            "Suite ID",
            testCase.suite_id
        );
        appendTestCaseReviewValue(
            reviewElement,
            "Suite Version",
            testCase.suite_version
        );
        appendTestCaseReviewValue(
            reviewElement,
            "Requirement Version ID",
            testCase.requirement_version_id
        );
    }
    appendTestCaseReviewList(
        reviewElement,
        "Preconditions",
        testCase.preconditions
    );
    appendTestCaseReviewList(
        reviewElement,
        "Steps",
        testCase.steps,
        true
    );
    appendTestCaseReviewValue(
        reviewElement,
        "Expected Result",
        testCase.expected_result
    );
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
            (item, index) => {

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
<tr data-test-case-filter-row
    data-search="${escapeHtml(`${item.id || ""} ${item.title || ""} ${item.requirement_version_id || ""} ${item.suite_id || ""}`.toLowerCase())}"
    data-priority="${escapeHtml(item.priority || "")}"
    data-test-type="${escapeHtml(item.test_type || "")}"
    data-automation-candidate="${isCandidate ? "yes" : "no"}">
<td>${checkbox}</td>
<td>${escapeHtml(item.id || "")}</td>
<td>${escapeHtml(item.title || "")}</td>
<td>${escapeHtml(item.priority || "")}</td>
<td>${escapeHtml(item.test_type || "")}</td>
<td>${isCandidate ? "Candidate" : "Manual-only"}</td>
<td>${escapeHtml(item.requirement_version_id || "")}</td>
<td>${escapeHtml(String(item.suite_version || ""))}</td>
<td>
<button
    type="button"
    data-review-test-case-index="${index}"
    aria-label="Review test case ${escapeHtml(item.id || "saved case")}"
>
    Review
</button>
</td>
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

    const priorities = Array.from(
        new Set(
            testCases
                .map(item => String(item.priority || "").trim())
                .filter(Boolean)
        )
    ).sort((left, right) => left.localeCompare(right));

    const testTypes = Array.from(
        new Set(
            testCases
                .map(item => String(item.test_type || "").trim())
                .filter(Boolean)
        )
    ).sort((left, right) => left.localeCompare(right));

    const projectName =
        project.name || project.project_id || projectId;

    const projectDetails = [
        project.application,
        project.environment,
    ].filter(Boolean).map(escapeHtml).join(" · ");

    const requirementCount = requirements.length;
    const testCaseCount = testCases.length;
    const candidateCount = testCases.filter(
        item => item.automation_candidate === true
    ).length;
    const artifactCount = automationArtifacts.length;

    const nextAction = testCaseCount === 0
        ? "Generate a QA suite from a project requirement."
        : candidateCount > 0 && artifactCount === 0
            ? "Select automation candidates and generate automation."
            : artifactCount > 0
                ? "Review generated automation or inspect recent executions."
                : "Review the saved test cases and available requirements.";

    const priorityOptions = priorities.map(value =>
        `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`
    ).join("");

    const testTypeOptions = testTypes.map(value =>
        `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`
    ).join("");

    resultElement.innerHTML = `
<header class="project-context-header">
    <h2>${escapeHtml(projectName)}</h2>
    <p>${projectDetails || `Project ID: ${escapeHtml(projectId)}`}</p>
    ${project.description
        ? `<p>${escapeHtml(project.description)}</p>`
        : ""}
</header>

<nav class="project-area-navigation" aria-label="Project areas" role="tablist">
    <button type="button" role="tab" aria-selected="true" aria-controls="project-area-overview" data-project-area="overview">Overview</button>
    <button type="button" role="tab" aria-selected="false" aria-controls="project-area-requirements" data-project-area="requirements">Requirements</button>
    <button type="button" role="tab" aria-selected="false" aria-controls="project-area-test-cases" data-project-area="test-cases">Test Cases <span>${testCaseCount}</span></button>
    <button type="button" role="tab" aria-selected="false" aria-controls="project-area-automation" data-project-area="automation">Automation <span>${artifactCount}</span></button>
    <button type="button" role="tab" aria-selected="false" aria-controls="project-area-executions" data-project-area="executions">Executions</button>
    <button type="button" role="tab" aria-selected="false" aria-controls="project-area-reports" data-project-area="reports">Reports</button>
</nav>

<section id="project-area-overview" class="project-area-panel" role="tabpanel" tabindex="0">
    <h3>Project Overview</h3>
    <div class="project-overview-grid">
        <div class="project-overview-card"><span>Requirement versions</span><strong>${requirementCount}</strong></div>
        <div class="project-overview-card"><span>Saved test cases</span><strong>${testCaseCount}</strong></div>
        <div class="project-overview-card"><span>Automation candidates</span><strong>${candidateCount}</strong></div>
        <div class="project-overview-card"><span>Generated artifacts</span><strong>${artifactCount}</strong></div>
        <div class="project-overview-card"><span>Executions</span><strong id="project-overview-execution-count">Loading</strong></div>
        <div class="project-overview-card"><span>Passed</span><strong id="project-overview-passed">Loading</strong></div>
        <div class="project-overview-card"><span>Failed</span><strong id="project-overview-failed">Loading</strong></div>
        <div class="project-overview-card"><span>Pass rate</span><strong id="project-overview-pass-rate">Loading</strong></div>
    </div>
    <div id="project-overview-activity" class="project-overview-activity" role="status">Loading recent project activity.</div>
    <div class="project-next-action">
        <strong>Suggested next action</strong>
        <p>${escapeHtml(nextAction)}</p>
        <button type="button" class="primary-button" data-project-next-action="requirements">Generate or review a QA suite</button>
    </div>
</section>

<section id="project-area-requirements" class="project-area-panel" role="tabpanel" tabindex="0" hidden>
    <h3>Requirements</h3>
    <form id="project-qa-generation-form" class="project-qa-generation-form">
        <label for="project-qa-requirement">Requirement</label>
        <textarea id="project-qa-requirement" rows="5" required placeholder="Describe the behavior this project needs to verify."></textarea>
        <button type="submit" class="primary-button" id="project-qa-generate-button">Generate QA Suite</button>
    </form>
    <div id="project-qa-generation-error" class="error" role="alert"></div>
    <div id="project-qa-generation-result" class="result-block"></div>
    <h4>Requirement Versions</h4>
    <div class="table-scroll"><table>
        <thead><tr><th>Version ID</th><th>Version</th><th>Requirement</th></tr></thead>
        <tbody>${requirementRows || '<tr><td colspan="3">No requirement versions have been saved.</td></tr>'}</tbody>
    </table></div>
    <h4>Saved Suite Versions</h4>
    <div class="table-scroll"><table>
        <thead><tr><th>Suite ID</th><th>Version</th><th>Requirement Version</th></tr></thead>
        <tbody>${suiteRows || '<tr><td colspan="3">No suite versions have been saved.</td></tr>'}</tbody>
    </table></div>
</section>

<section id="project-area-test-cases" class="project-area-panel" role="tabpanel" tabindex="0" hidden>
    <h3>Saved Test Cases</h3>
    <div class="test-case-filters" aria-label="Filter saved test cases">
        <label>Search<input id="saved-test-case-search" type="search" placeholder="Search ID or title"></label>
        <label>Priority<select id="saved-test-case-priority"><option value="">All priorities</option>${priorityOptions}</select></label>
        <label>Type<select id="saved-test-case-type"><option value="">All types</option>${testTypeOptions}</select></label>
        <label>Automation suitability<select id="saved-test-case-candidate"><option value="">All cases</option><option value="yes">Candidates</option><option value="no">Manual-only</option></select></label>
    </div>
    <p id="saved-test-case-count" class="filter-result-count" role="status">${testCaseCount} test cases</p>
    <div class="table-scroll"><table>
        <thead><tr><th>Select</th><th>ID</th><th>Title</th><th>Priority</th><th>Type</th><th>Suitability</th><th>Requirement Version</th><th>Suite Version</th><th>Actions</th></tr></thead>
        <tbody>${testCaseRows || '<tr><td colspan="9">No saved test cases are available for this project.</td></tr>'}</tbody>
    </table></div>
    <section id="project-test-case-review" class="test-case-review" aria-live="polite" hidden></section>
</section>

<section id="project-area-automation" class="project-area-panel" role="tabpanel" tabindex="0" hidden>
    <h3>Automation</h3>
    <p>Choose persisted test-case candidates to generate automation. Review and execution are separate actions.</p>
    <h4>Generated Automation Artifacts</h4>
    <div class="table-scroll"><table>
        <thead><tr><th>Artifact ID</th><th>Test Case</th><th>Automation Case</th><th>Framework</th><th>Language</th><th>Actions</th></tr></thead>
        <tbody>${artifactRows || '<tr><td colspan="6">No automation artifacts have been generated for this project.</td></tr>'}</tbody>
    </table></div>
    <section id="project-artifact-review" class="artifact-review" aria-live="polite" hidden></section>
</section>

`;

    const automationArea = document.getElementById(
        "project-area-automation"
    );
    const workspaceAction = document.getElementById(
        "project-workspace-action"
    );
    if (automationArea && workspaceAction) {
        automationArea.appendChild(workspaceAction);
    }

    const areaTabs = Array.from(
        resultElement.querySelectorAll("[data-project-area]")
    );
    areaTabs.forEach((tab, index) => {
        tab.addEventListener("click", () => {
            setProjectWorkspaceArea(tab.dataset.projectArea);
        });
        tab.addEventListener("keydown", event => {
            if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") {
                return;
            }
            event.preventDefault();
            const offset = event.key === "ArrowRight" ? 1 : -1;
            const nextTab = areaTabs[
                (index + offset + areaTabs.length) % areaTabs.length
            ];
            nextTab.focus();
            nextTab.click();
        });
    });

    setProjectWorkspaceArea("overview");
    resultElement.querySelectorAll("[data-project-next-action]")
        .forEach(button => {
            button.addEventListener("click", () => {
                setProjectWorkspaceArea(button.dataset.projectNextAction);
                document.getElementById("project-qa-requirement").focus();
            });
        });
    document.getElementById("project-qa-generation-form")
        .addEventListener("submit", generateProjectQASuite);
    document.querySelectorAll(
        "#saved-test-case-search, #saved-test-case-priority, " +
        "#saved-test-case-type, #saved-test-case-candidate"
    ).forEach(control => {
        control.addEventListener("input", applySavedTestCaseFilters);
        control.addEventListener("change", applySavedTestCaseFilters);
    });
    applySavedTestCaseFilters();

    const testCaseReviewElement = document.getElementById(
        "project-test-case-review"
    );

    resultElement
        .querySelectorAll("[data-review-test-case-index]")
        .forEach(button => {
            button.addEventListener("click", () => {
                const index = Number(
                    button.dataset.reviewTestCaseIndex
                );
                const testCase = testCases[index];

                if (!testCase || !testCaseReviewElement) {
                    return;
                }

                renderProjectTestCaseReview(
                    testCase,
                    testCaseReviewElement
                );
            });
        });

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

    setProjectWorkspaceArea("executions");

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
        updateProjectOverview(report, analysis);
    } catch (error) {
        renderProjectOverviewError(
            error.message ||
            "Unable to load project execution overview."
        );
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
