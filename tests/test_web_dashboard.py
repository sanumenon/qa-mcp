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

    # JavaScript action wiring remains in the HTML.
    assert "onclick=\"createQAProject()\"" in html
    assert "onclick=\"generateQASuite()\"" in html

    # Static JavaScript asset is now responsible for
    # backend API wiring.
    assert '<script src="/static/js/dashboard.js"></script>' in html

    # Result/error areas
    assert 'id="project-error"' in html
    assert 'id="project-success"' in html
    assert 'id="qa-workspace-error"' in html
    assert 'id="qa-workspace-result"' in html


def test_dashboard_javascript_contains_backend_api_wiring():
    response = client.get("/static/js/dashboard.js")

    assert response.status_code == 200

    javascript = response.text

    # Project APIs
    assert 'fetch("/api/projects")' in javascript
    assert '"/api/projects/"' in javascript

    # QA suite generation API
    assert '"/qa-suite"' in javascript

    # Core UI functions
    assert "async function loadQAProjects" in javascript
    assert "async function createQAProject" in javascript
    assert "async function generateQASuite" in javascript
    assert "function renderQASuite" in javascript
    assert "async function loadDashboard" in javascript
    assert '"/qa-suite/save"' in javascript
    assert "Save Selected Test Cases" in javascript
    assert "Select All" in javascript
    assert "Clear All" in javascript

    assert (
        "async function saveSelectedTestCases"
        in javascript
    )

    assert (
        "function toggleAllTestCases"
        in javascript
    )

    assert (
        "function updateSelectedTestCaseCount"
        in javascript
    )

    assert (
        "function getSelectedTestCaseIds"
        in javascript
    )

def test_dashboard_static_assets_are_served():
    css_response = client.get(
        "/static/css/dashboard.css"
    )

    assert css_response.status_code == 200
    assert "text/css" in (
        css_response.headers.get("content-type") or ""
    )
    assert "body {" in css_response.text

    js_response = client.get(
        "/static/js/dashboard.js"
    )

    assert js_response.status_code == 200
    assert "javascript" in (
        js_response.headers.get("content-type") or ""
    )
    assert "function escapeHtml" in js_response.text

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
            generated_suite = {
                "project": {
                    "project_id": "qa-project",
                    "name": "Customer Portal QA",
                },
                "requirement_version": {
                    "version_id": "REQ-001",
                    "version": 1,
                },
                "suite_version": None,
                "requirement": {
                    "requirement": "User can reset password.",
                    "application": "Customer Portal",
                },
                "analysis": {
                    "summary": "Password reset workflow.",
                    "actors": ["User"],
                    "functional_requirements": [
                        "User can request a password reset."
                    ],
                    "positive_scenarios": [
                        "Valid password reset request succeeds."
                    ],
                    "negative_scenarios": [
                        "Invalid reset request is rejected."
                    ],
                    "edge_cases": [
                        "Expired reset link is rejected."
                    ],
                },
                "test_cases": {
                    "test_cases": [
                        {
                            "id": "TC-001",
                            "title": "Reset password",
                            "priority": "High",
                            "test_type": "Functional",
                            "preconditions": [],
                            "steps": [
                                "Request password reset"
                            ],
                            "expected_result": (
                                "Password reset succeeds"
                            ),
                        },
                        {
                            "id": "TC-002",
                            "title": "Reject invalid reset request",
                            "priority": "Medium",
                            "test_type": "Negative",
                            "preconditions": [],
                            "steps": [
                                "Submit invalid reset request"
                            ],
                            "expected_result": (
                                "Invalid request is rejected"
                            ),
                        },
                        {
                            "id": "TC-003",
                            "title": "Reject expired reset link",
                            "priority": "Medium",
                            "test_type": "Edge",
                            "preconditions": [],
                            "steps": [
                                "Open expired reset link"
                            ],
                            "expected_result": (
                                "Expired link is rejected"
                            ),
                        },
                    ]
                },
                "review": {
                    "overall_quality": "Good",
                    "coverage_score": 90,
                    "duplicate_test_cases": [],
                    "missing_scenarios": [],
                    "weak_test_cases": [],
                    "requirement_gaps": [],
                    "priority_issues": [],
                    "recommendations": [],
                    "summary": "Good coverage.",
                },
            }

            save_requests = []

            def handle_save_request(route):
                import json

                request_payload = json.loads(
                    route.request.post_data
                )

                save_requests.append(request_payload)

                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps(
                        {
                            "suite_id": "SUITE-002",
                            "project_id": "qa-project",
                            "version": len(save_requests) + 1,
                        }
                    ),
                )

            def handle_projects_request(route):
                import json

                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps(
                        [
                            {
                                "project_id": "qa-project",
                                "name": "Customer Portal QA",
                                "description": "",
                                "application": "Customer Portal",
                                "environment": "test",
                                "metadata": {},
                            }
                        ]
                    ),
                )

            def handle_generate_request(route):
                import json

                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps(generated_suite),
                )

            page.route(
                "**/api/projects",
                handle_projects_request,
            )

            page.route(
                "**/api/projects/qa-project/qa-suite",
                handle_generate_request,
            )

            page.route(
                "**/api/projects/qa-project/qa-suite/save",
                handle_save_request,
            )

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
            # Generate a deterministic QA suite through the
            # existing UI.
            page.locator(
                "#qa-project-id"
            ).select_option("qa-project")

            page.locator(
                "#qa-requirement"
            ).fill(
                "User can reset password."
            )

            page.get_by_role(
                "button",
                name="Generate QA Suite",
            ).click()

            page.get_by_role(
                "heading",
                name="Generated Test Cases",
            ).wait_for()

            test_case_checkboxes = page.locator(
                ".qa-test-case-checkbox"
            )

            assert test_case_checkboxes.count() == 3

            assert page.locator(
                "#qa-selected-test-case-count"
            ).inner_text().strip() == "3"

            # Clear all generated test cases.
            page.get_by_role(
                "button",
                name="Clear All",
            ).click()

            assert page.locator(
                "#qa-selected-test-case-count"
            ).inner_text().strip() == "0"

            # Select only TC-001 and TC-003.
            page.locator(
                '.qa-test-case-checkbox[value="TC-001"]'
            ).check()

            page.locator(
                '.qa-test-case-checkbox[value="TC-003"]'
            ).check()

            assert page.locator(
                "#qa-selected-test-case-count"
            ).inner_text().strip() == "2"

            # Save only the selected cases.
            page.get_by_role(
                "button",
                name="Save Selected Test Cases",
            ).click()

            page.locator(
                "#qa-save-success"
            ).wait_for()

            assert page.locator(
                "#qa-save-success"
            ).inner_text() == (
                "2 test cases saved successfully."
            )

            assert len(save_requests) == 1

            assert save_requests[0][
                "selected_test_case_ids"
            ] == [
                "TC-001",
                "TC-003",
            ]

            # Select all generated cases and save again.
            page.get_by_role(
                "button",
                name="Select All",
            ).click()

            assert page.locator(
                "#qa-selected-test-case-count"
            ).inner_text().strip() == "3"

            page.get_by_role(
                "button",
                name="Save Selected Test Cases",
            ).click()

            page.locator(
                "#qa-save-success"
            ).wait_for()

            assert page.locator(
                "#qa-save-success"
            ).inner_text() == (
                "3 test cases saved successfully."
            )

            assert len(save_requests) == 2

            assert save_requests[1][
                "selected_test_case_ids"
            ] == [
                "TC-001",
                "TC-002",
                "TC-003",
            ]
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

def test_save_selected_test_cases_endpoint():
    with patch(
        "qa_mcp.web.app.qa_workspace_service"
    ) as service:

        service.save_selected_test_cases.return_value = {
            "suite_id": "SUITE-002",
            "project_id": "qa-project",
            "version": 2,
        }

        response = client.post(
            "/api/projects/qa-project/qa-suite/save",
            json={
                "requirement_version_id": "REQ-001",
                "test_cases": {
                    "test_cases": [
                        {
                            "id": "TC-001",
                            "title": "Reset password",
                            "priority": "High",
                            "test_type": "Functional",
                            "preconditions": [],
                            "steps": [
                                "Request password reset"
                            ],
                            "expected_result": (
                                "Password reset succeeds"
                            ),
                        }
                    ]
                },
                "review": {
                    "overall_quality": "Good",
                    "coverage_score": 90,
                    "duplicate_test_cases": [],
                    "missing_scenarios": [],
                    "weak_test_cases": [],
                    "requirement_gaps": [],
                    "priority_issues": [],
                    "recommendations": [],
                    "summary": "Good coverage.",
                },
                "selected_test_case_ids": [
                    "TC-001"
                ],
            },
        )

        assert response.status_code == 200

        assert response.json() == {
            "suite_id": "SUITE-002",
            "project_id": "qa-project",
            "version": 2,
        }

        service.save_selected_test_cases.assert_called_once_with(
            project_id="qa-project",
            requirement_version_id="REQ-001",
            test_cases={
                "test_cases": [
                    {
                        "id": "TC-001",
                        "title": "Reset password",
                        "priority": "High",
                        "test_type": "Functional",
                        "preconditions": [],
                        "steps": [
                            "Request password reset"
                        ],
                        "expected_result": (
                            "Password reset succeeds"
                        ),
                    }
                ]
            },
            review={
                "overall_quality": "Good",
                "coverage_score": 90,
                "duplicate_test_cases": [],
                "missing_scenarios": [],
                "weak_test_cases": [],
                "requirement_gaps": [],
                "priority_issues": [],
                "recommendations": [],
                "summary": "Good coverage.",
            },
            selected_test_case_ids=[
                "TC-001"
            ],
        )

def test_save_selected_test_cases_rejects_empty_selection():
    response = client.post(
        "/api/projects/qa-project/qa-suite/save",
        json={
            "requirement_version_id": "REQ-001",
            "test_cases": {
                "test_cases": []
            },
            "review": {
                "overall_quality": "Good",
                "coverage_score": 90,
                "duplicate_test_cases": [],
                "missing_scenarios": [],
                "weak_test_cases": [],
                "requirement_gaps": [],
                "priority_issues": [],
                "recommendations": [],
                "summary": "Good coverage.",
            },
            "selected_test_case_ids": [],
        },
    )

    assert response.status_code == 422