from unittest.mock import patch

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
                "summary": (
                    "Password reset workflow."
                )
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
                "Project already exists: "
                "customer-portal"
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

def test_dashboard_contains_ai_qa_workspace_controls():
    response = client.get("/")

    assert response.status_code == 200

    html = response.text

    # Core AI QA Workspace UI
    assert "AI QA Workspace" in html
    assert "Create QA Project" in html
    assert "Generate QA Suite" in html

    # Project creation controls
    assert 'id="project-id"' in html
    assert 'id="project-name"' in html
    assert 'id="project-application"' in html
    assert 'id="project-environment"' in html
    assert 'id="project-description"' in html

    # QA generation controls
    assert 'id="qa-project-id"' in html
    assert 'id="qa-requirement"' in html

    # JavaScript action wiring
    assert "onclick=\"createQAProject()\"" in html
    assert "onclick=\"generateQASuite()\"" in html

    # Backend API wiring
    assert '"/api/projects"' in html
    assert '"/api/projects/"' in html
    assert '"/qa-suite"' in html

    # Result/error areas
    assert 'id="project-error"' in html
    assert 'id="project-success"' in html
    assert 'id="qa-workspace-error"' in html
    assert 'id="qa-workspace-result"' in html

def test_dashboard_ai_qa_workspace_browser_flow():
    import threading
    import time

    import uvicorn
    from playwright.sync_api import sync_playwright

    server = uvicorn.Server(
        uvicorn.Config(
            "qa_mcp.web.app:app",
            host="127.0.0.1",
            port=8765,
            log_level="error",
        )
    )

    thread = threading.Thread(
        target=server.run,
        daemon=True,
    )

    thread.start()

    try:
        deadline = time.time() + 10

        while not server.started:
            if time.time() >= deadline:
                raise AssertionError(
                    "Uvicorn server did not start within 10 seconds"
                )

            time.sleep(0.05)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            page.goto(
                "http://127.0.0.1:8765/",
                wait_until="networkidle",
            )

            # Verify the actual rendered dashboard.
            assert page.title() == "QA MCP Dashboard"

            assert page.get_by_role(
                "heading",
                name="AI QA Workspace",
            ).is_visible()

            assert page.get_by_role(
                "button",
                name="Create QA Project",
            ).is_visible()

            assert page.get_by_role(
                "button",
                name="Generate QA Suite",
            ).is_visible()

            # Verify the important workspace controls exist
            # in the rendered DOM.
            assert page.locator(
                "#project-id"
            ).is_visible()

            assert page.locator(
                "#project-name"
            ).is_visible()

            assert page.locator(
                "#project-application"
            ).is_visible()

            assert page.locator(
                "#project-environment"
            ).is_visible()

            assert page.locator(
                "#qa-project-id"
            ).is_visible()

            assert page.locator(
                "#qa-requirement"
            ).is_visible()

            # Verify the execution dashboard has not disappeared.
            assert page.get_by_role(
                "heading",
                name="Automation Execution Overview",
            ).is_visible()

            browser.close()

    finally:
        server.should_exit = True
        thread.join(timeout=5)

        if thread.is_alive():
            raise AssertionError(
                "Uvicorn server did not shut down cleanly"
            )