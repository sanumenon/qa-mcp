function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


async function loadExecutionPage() {

    const errorElement =
        document.getElementById(
            "execution-error"
        );

    try {

        const reportResponse =
            await fetch(
                "/api/executions/report"
            );

        const report =
            await reportResponse.json();

        if (!reportResponse.ok) {
            throw new Error(
                report.detail ||
                "Unable to load execution report."
            );
        }

        document.getElementById(
            "execution-total"
        ).textContent =
            report.total_executions;

        document.getElementById(
            "execution-passed"
        ).textContent =
            report.passed;

        document.getElementById(
            "execution-failed"
        ).textContent =
            report.failed;

        document.getElementById(
            "execution-errors"
        ).textContent =
            report.error;


        const executionsResponse =
            await fetch(
                "/api/executions?limit=20"
            );

        const executions =
            await executionsResponse.json();

        if (!executionsResponse.ok) {
            throw new Error(
                executions.detail ||
                "Unable to load executions."
            );
        }


        const executionBody =
            document.getElementById(
                "execution-body"
            );

        executionBody.innerHTML =
            executions.map(
                item => `
<tr>
<td>
${escapeHtml(item.execution_id)}
</td>

<td>
${escapeHtml(item.automation_case_id)}
</td>

<td class="status-${escapeHtml(item.status)}">
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

    } catch (error) {

        console.error(
            "Execution page loading failed:",
            error
        );

        errorElement.textContent =
            error.message ||
            "Unable to load execution data.";
    }
}


loadExecutionPage();