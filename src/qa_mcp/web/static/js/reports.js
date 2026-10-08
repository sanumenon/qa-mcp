function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


async function loadReportsPage() {

    const errorElement =
        document.getElementById(
            "reports-error"
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
            "report-total"
        ).textContent =
            report.total_executions;


        document.getElementById(
            "report-pass-rate"
        ).textContent =
            Number(
                report.pass_rate_percent
            ).toFixed(1) + "%";


        document.getElementById(
            "report-average-duration"
        ).textContent =
            Number(
                report.average_duration_seconds
            ).toFixed(2) + "s";


        const failuresResponse =
            await fetch(
                "/api/executions/failures?limit=20"
            );

        const failures =
            await failuresResponse.json();

        if (!failuresResponse.ok) {
            throw new Error(
                failures.detail ||
                "Unable to load failure analysis."
            );
        }


        const failureBody =
            document.getElementById(
                "failure-body"
            );

        failureBody.innerHTML =
            failures.failures.map(
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
${escapeHtml(item.message)}
</td>
</tr>
`
            ).join("");

    } catch (error) {

        console.error(
            "Reports page loading failed:",
            error
        );

        errorElement.textContent =
            error.message ||
            "Unable to load reports.";
    }
}


loadReportsPage();