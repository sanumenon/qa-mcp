from fastapi.testclient import TestClient

from qa_mcp.web.app import app


client = TestClient(app)


def test_dashboard_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "application": "QA MCP Dashboard",
    }


def test_dashboard_page():
    response = client.get("/")

    assert response.status_code == 200
    assert "QA MCP Dashboard" in response.text
    assert "Recent Executions" in response.text
    assert "Failures" in response.text


def test_executions_endpoint():
    response = client.get(
        "/api/executions?limit=5"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_execution_report_endpoint():
    response = client.get(
        "/api/executions/report"
    )

    assert response.status_code == 200

    payload = response.json()

    assert "total_executions" in payload
    assert "passed" in payload
    assert "failed" in payload
    assert "error" in payload
    assert "pass_rate_percent" in payload
    assert "average_duration_seconds" in payload


def test_execution_failure_endpoint():
    response = client.get(
        "/api/executions/failures"
    )

    assert response.status_code == 200

    payload = response.json()

    assert "total_executions" in payload
    assert "total_failures" in payload
    assert "failure_rate_percent" in payload
    assert "failures" in payload
