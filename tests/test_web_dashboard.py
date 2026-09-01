from fastapi.testclient import TestClient

from qa_mcp.web.app import app

from unittest.mock import patch

from qa_mcp.models.schemas import (
    QASuiteResult,
)

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

def test_qa_workspace_endpoint():
    with patch(
        "qa_mcp.web.app.qa_workspace_service"
    ) as service:

        service.generate_qa_suite.return_value = {
            "project": {
                "project_id": "qa-project"
            },
            "requirement_version": {
                "version_id": "REQ-001"
            },
            "suite_version": {
                "suite_id": "SUITE-001"
            },
            "requirement": {
                "requirement": (
                    "User can reset password."
                ),
                "application": "Customer Portal",
            },
            "analysis": {
                "summary": "Password reset workflow."
            },
            "test_cases": {
                "test_cases": []
            },
            "review": {
                "coverage_score": 90
            },
        }

        response = client.post(
            "/api/projects/qa-project/qa-suite",
            json={
                "requirement": (
                    "User can reset password."
                )
            },
        )

        assert response.status_code == 200

        payload = response.json()

        assert (
            payload["project"]["project_id"]
            == "qa-project"
        )

        assert (
            payload["suite_version"]["suite_id"]
            == "SUITE-001"
        )

        service.generate_qa_suite.assert_called_once_with(
            project_id="qa-project",
            requirement=(
                "User can reset password."
            ),
        )


def test_qa_workspace_rejects_empty_requirement():
    response = client.post(
        "/api/projects/qa-project/qa-suite",
        json={
            "requirement": ""
        },
    )

    assert response.status_code == 422

def test_create_qa_project_endpoint():

    with patch(
        "qa_mcp.web.app.qa_workspace_service"
    ) as service:

        service.create_project.return_value = {
            "project_id": "customer-portal",
            "name": "Customer Portal QA",
            "description": "",
            "application": "Customer Portal",
            "environment": "test",
            "metadata": {},
        }

        response = client.post(
            "/api/projects",
            json={
                "project_id": "customer-portal",
                "name": "Customer Portal QA",
                "application": "Customer Portal",
                "environment": "test",
            },
        )

        assert response.status_code == 200

        payload = response.json()

        assert (
            payload["project_id"]
            == "customer-portal"
        )

        service.create_project.assert_called_once_with(
            project_id="customer-portal",
            name="Customer Portal QA",
            application="Customer Portal",
            environment="test",
            description="",
            metadata={},
        )


def test_create_qa_project_rejects_empty_project_id():

    response = client.post(
        "/api/projects",
        json={
            "project_id": "",
            "name": "Customer Portal QA",
            "application": "Customer Portal",
            "environment": "test",
        },
    )

    assert response.status_code == 422


def test_create_qa_project_duplicate_returns_conflict():

    with patch(
        "qa_mcp.web.app.qa_workspace_service"
    ) as service:

        service.create_project.side_effect = (
            ValueError(
                "Project already exists: customer-portal"
            )
        )

        response = client.post(
            "/api/projects",
            json={
                "project_id": "customer-portal",
                "name": "Customer Portal QA",
                "application": "Customer Portal",
                "environment": "test",
            },
        )

        assert response.status_code == 409

        assert response.json()["detail"] == (
            "Project already exists: "
            "customer-portal"
        )
