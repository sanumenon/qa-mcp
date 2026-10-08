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

def test_execution_page():
    response = client.get("/execution")

    assert response.status_code == 200

    html = response.text

    assert "QA MCP — Execution" in html
    assert "<h1>Execution</h1>" in html
    assert "Recent Executions" in html
    assert (
        '<script src="/static/js/execution.js"></script>'
        in html
    )

    assert (
        'href="/project-workspace"'
        in html
    )

    assert (
        'href="/reports"'
        in html
    )


def test_reports_page():
    response = client.get("/reports")

    assert response.status_code == 200

    html = response.text

    assert (
        "QA MCP — Reports &amp; Analysis"
        in html
    )

    assert (
        "<h1>Reports &amp; Analysis</h1>"
        in html
    )

    assert "Failure Analysis" in html

    assert (
        '<script src="/static/js/reports.js"></script>'
        in html
    )

    assert (
        'href="/execution"'
        in html
    )


def test_workflow_navigation_is_present_on_existing_pages():
    dashboard_response = client.get("/")

    assert dashboard_response.status_code == 200

    dashboard_html = dashboard_response.text

    assert (
        'class="workflow-navigation"'
        in dashboard_html
    )

    assert (
        'href="/project-workspace"'
        in dashboard_html
    )

    assert (
        'href="/execution"'
        in dashboard_html
    )

    assert (
        'href="/reports"'
        in dashboard_html
    )


    workspace_response = client.get(
        "/project-workspace"
    )

    assert workspace_response.status_code == 200

    workspace_html = workspace_response.text

    assert (
        'class="workflow-navigation"'
        in workspace_html
    )

    assert (
        'href="/"'
        in workspace_html
    )

    assert (
        'href="/execution"'
        in workspace_html
    )

    assert (
        'href="/reports"'
        in workspace_html
    )


def test_workflow_static_assets_are_served():

    execution_response = client.get(
        "/static/js/execution.js"
    )

    assert execution_response.status_code == 200

    assert (
        "loadExecutionPage"
        in execution_response.text
    )

    assert (
        "/api/executions/report"
        in execution_response.text
    )


    reports_response = client.get(
        "/static/js/reports.js"
    )

    assert reports_response.status_code == 200

    assert (
        "loadReportsPage"
        in reports_response.text
    )

    assert (
        "/api/executions/failures"
        in reports_response.text
    )


    css_response = client.get(
        "/static/css/dashboard.css"
    )

    assert css_response.status_code == 200

    assert (
        ".workflow-navigation"
        in css_response.text
    )

    assert (
        ".workflow-nav-link"
        in css_response.text
    )

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

def test_qa_workspace_returns_502_for_llm_generation_failure():
    with patch(
        "qa_mcp.web.app.qa_workspace_service"
    ) as service:

        from qa_mcp.core.llm import LLMGenerationError

        service.generate_qa_suite.side_effect = LLMGenerationError(
            "LLM returned an unusable response for test-case generation."
        )

        response = client.post(
            "/api/projects/qa-project/qa-suite",
            json={
                "requirement": (
                    "User can reset password."
                )
            },
        )

        assert response.status_code == 502

        assert response.json() == {
            "detail": (
                "LLM returned an unusable response "
                "for test-case generation."
            )
        }

        service.generate_qa_suite.assert_called_once_with(
            project_id="qa-project",
            requirement=(
                "User can reset password."
            ),
        )


def test_qa_project_workspace_endpoint():
    with patch(
        "qa_mcp.web.app.qa_workspace_service"
    ) as service:

        service.get_project_qa_workspace.return_value = {
            "project": {
                "project_id": "qa-project"
            },
            "requirement_versions": [
                {
                    "version_id": "REQ-001"
                }
            ],
            "suite_versions": [
                {
                    "suite_id": "SUITE-001",
                    "version": 1,
                }
            ],
            "test_cases": [
                {
                    "id": "TC-001",
                    "title": "Reset password",
                    "suite_id": "SUITE-001",
                    "suite_version": 1,
                    "requirement_version_id": "REQ-001",
                    "automation_candidate": True,
                }
            ],
            "automation_artifacts": [
                {
                    "artifact_id": "ART-001",
                    "test_case_id": "TC-001",
                }
            ],
        }

        response = client.get(
            "/api/projects/qa-project/workspace"
        )

        assert response.status_code == 200

        payload = response.json()

        assert (
            payload["project"]["project_id"]
            == "qa-project"
        )

        assert (
            payload["requirement_versions"][0][
                "version_id"
            ]
            == "REQ-001"
        )

        assert (
            payload["suite_versions"][0][
                "suite_id"
            ]
            == "SUITE-001"
        )

        assert (
            payload["test_cases"][0]["id"]
            == "TC-001"
        )

        assert (
            payload["test_cases"][0][
                "automation_candidate"
            ]
            is True
        )

        assert (
            payload["automation_artifacts"][0][
                "artifact_id"
            ]
            == "ART-001"
        )

        service.get_project_qa_workspace.assert_called_once_with(
            "qa-project"
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

    # JavaScript action wiring is handled by the static dashboard.js asset.
    assert 'id="create-qa-project-button"' in html
    assert 'id="generate-qa-suite-button"' in html

    # Static JavaScript asset is now responsible for
    # backend API wiring.
    assert '<script src="/static/js/dashboard.js"></script>' in html

    # Result/error areas
    assert 'id="project-error"' in html
    assert 'id="project-success"' in html
    assert 'id="qa-workspace-error"' in html
    assert 'id="qa-workspace-result"' in html

def test_project_qa_workspace_page_contains_repository_controls():
    response = client.get(
        "/project-workspace"
    )

    assert response.status_code == 200

    html = response.text

    assert "Project QA Workspace" in html

    assert (
        'id="repository-project-id"'
        in html
    )

    assert (
        'id="load-project-workspace-button"'
        in html
    )

    assert (
        "loadProjectQAWorkspace()"
        in html
    )

    assert (
        'id="project-workspace-result"'
        in html
    )

    assert (
        'id="project-execution-insights"'
        in html
    )

    assert (
        "/static/js/project_workspace.js"
        in html
    )

def test_dashboard_retains_generate_qa_suite_control():
    response = client.get("/")

    assert response.status_code == 200

    html = response.text

    assert (
        'id="generate-qa-suite-button"'
        in html
    )

    assert (
        "Generate QA Suite"
        in html
    )

    assert (
        'onclick="generateQASuite()"'
        in html
    )

    assert (
        "/project-workspace"
        in html
    )

def test_project_qa_workspace_javascript_is_served():
    response = client.get(
        "/static/js/project_workspace.js"
    )

    assert response.status_code == 200

    javascript = response.text

    assert (
        "loadProjectQAWorkspace"
        in javascript
    )

    assert (
        "loadProjectExecutionInsights"
        in javascript
    )

    assert (
        'fetch(projectPath + "/report")'
        in javascript
    )

    assert (
        'fetch(projectPath + "/failures?limit=10")'
        in javascript
    )

    assert (
        "/api/projects/"
        in javascript
    )

    assert (
        "/workspace"
        in javascript
    )


    assert "const testCasesPayload =" in javascript
    assert "Array.isArray(testCasesPayload)" in javascript
    assert "testCasesPayload.test_cases || []" in javascript


def test_dashboard_javascript_contains_backend_api_wiring():
    response = client.get("/static/js/dashboard.js")

    assert response.status_code == 200

    javascript = response.text

    # Project APIs
    assert 'fetch("/api/projects")' in javascript
    assert '"/api/projects/"' in javascript

    # QA suite generation API
    assert '"/qa-suite"' in javascript
    assert "generateQASuite()" in javascript
    assert "button.disabled = true" in javascript
    assert "button.disabled = false" in javascript

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
    assert "Generating QA Suite..." in javascript
    assert "button.disabled = true" in javascript
    assert "button.disabled = false" in javascript
    assert "finally" in javascript

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
    from playwright.sync_api import expect, sync_playwright

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

            assert page.locator(
                "#generate-qa-suite-button"
            ).is_visible()

            assert page.locator(
                "#generate-qa-suite-button"
            ).is_enabled()

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

            expect(
                page.locator("#open-project-workspace-link")
            ).to_be_visible()
            expect(
                page.locator("#open-project-workspace-link")
            ).to_have_attribute(
                "href",
                "/project-workspace?project_id=qa-project",
            )

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

            assert "2 test cases saved successfully." in page.locator(
                "#qa-save-success"
            ).inner_text()
            expect(
                page.locator("#qa-save-success a")
            ).to_have_attribute(
                "href",
                "/project-workspace?project_id=qa-project",
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

            assert "3 test cases saved successfully." in page.locator(
                "#qa-save-success"
            ).inner_text()

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

def test_project_automation_generation_endpoint():
    with patch(
        "qa_mcp.web.app.qa_workspace_service"
    ) as service:

        service.generate_automation_from_project.return_value = {
            "project": {
                "project_id": "qa-project",
                "name": "QA Project",
            },
            "selected_test_case_ids": [
                "TC-001",
                "TC-002",
            ],
            "automation_candidates": {
                "candidate_ids": [
                    "TC-001",
                    "TC-002",
                ],
                "manual_ids": [],
                "total": 2,
            },
            "automation_cases": [
                {
                    "id": "AUTO-001",
                    "test_case_id": "TC-001",
                },
            ],
            "automation_artifacts": [
                {
                    "artifact_id": "ART-001",
                    "test_case_id": "TC-001",
                },
            ],
        }

        response = client.post(
            "/api/projects/qa-project/automation",
            json={
                "selected_test_case_ids": [
                    "TC-001",
                    "TC-002",
                ],
            },
        )

        assert response.status_code == 200

        payload = response.json()

        assert payload["selected_test_case_ids"] == [
            "TC-001",
            "TC-002",
        ]

        assert payload["automation_candidates"][
            "candidate_ids"
        ] == [
            "TC-001",
            "TC-002",
        ]

        service.generate_automation_from_project.assert_called_once_with(
            project_id="qa-project",
            selected_test_case_ids=[
                "TC-001",
                "TC-002",
            ],
        )


def test_project_automation_generation_rejects_empty_selection():
    response = client.post(
        "/api/projects/qa-project/automation",
        json={
            "selected_test_case_ids": [],
        },
    )

    assert response.status_code == 422


def test_project_qa_workspace_page_contains_automation_action():
    response = client.get(
        "/project-workspace"
    )

    assert response.status_code == 200

    html = response.text

    assert (
        'id="generate-project-automation-button"'
        in html
    )

    assert (
        "generateProjectAutomation()"
        in html
    )


def test_project_qa_workspace_javascript_contains_automation_wiring():
    response = client.get(
        "/static/js/project_workspace.js"
    )

    assert response.status_code == 200

    javascript = response.text

    assert (
        "generateProjectAutomation"
        in javascript
    )

    assert (
        'selected_test_case_ids'
        in javascript
    )

    assert (
        '"/automation"'
        in javascript
    )

    assert (
        'data-automation-candidate="true"'
        in javascript
    )

    assert (
        "updateProjectAutomationButton"
        in javascript
    )

    assert (
        "executeProjectAutomation"
        in javascript
    )

    assert "data-review-artifact" in javascript
    assert "project-artifact-review" in javascript
    assert "source.textContent" in javascript

    assert (
        "/automation/"
        in javascript
    )

    assert (
        "/execute"
        in javascript
    )


def test_project_workspace_execution_insights_browser_flow():
    import json
    import threading
    import time

    import uvicorn
    from playwright.sync_api import expect, sync_playwright

    server = uvicorn.Server(
        uvicorn.Config(
            "qa_mcp.web.app:app",
            host="127.0.0.1",
            port=8766,
            log_level="error",
        )
    )
    thread = threading.Thread(
        target=server.run,
        daemon=True,
    )
    thread.start()

    workspace_payload = {
        "project": {
            "project_id": "insights-project",
            "name": "Insights Project",
            "application": "QA app",
            "environment": "test",
        },
        "requirement_versions": [],
        "suite_versions": [],
        "test_cases": [
            {
                "id": "TC-INSIGHT-1",
                "title": "Reviewable case",
                "priority": "High",
                "test_type": "Functional",
                "preconditions": [
                    "User is signed in",
                    "Account is active",
                ],
                "steps": [
                    "Open the sign-in page",
                    "Submit valid credentials",
                ],
                "expected_result": "Dashboard appears",
                "automation_candidate": True,
                "suite_id": "SUITE-INSIGHT-1",
                "suite_version": 1,
                "requirement_version_id": "REQ-INSIGHT-1",
            },
            {
                "id": "TC-INSIGHT-2",
                "title": '<img src="x" onerror="window.caseTitleRan=true">',
                "priority": "Critical",
                "test_type": "Security",
                "preconditions": [
                    "<script>window.caseExecuted=true;</script>"
                ],
                "steps": [
                    "<b>First hostile step</b>",
                    '<img src="x" onerror="window.caseStepRan=true">',
                ],
                "expected_result": (
                    '<svg onload="window.caseExpectedRan=true">'
                ),
                "automation_candidate": True,
                "suite_id": "SUITE-INSIGHT-2",
                "suite_version": 2,
                "requirement_version_id": "REQ-INSIGHT-2",
            },
        ],
        "automation_artifacts": [
            {
                "artifact_id": "ART-INSIGHT-1",
                "test_case_id": "TC-INSIGHT-1",
                "automation_case_id": "AC-INSIGHT-1",
                "framework": "Playwright",
                "language": "Python",
                "file_name": "test_reviewable.py",
                "created_at": "2026-01-02T03:04:05+00:00",
                "code": (
                    "<script>window.artifactExecuted = true;</script>\n"
                    "print('safe')"
                ),
            },
            {
                "artifact_id": "ART-INSIGHT-2",
                "test_case_id": "TC-INSIGHT-1",
                "automation_case_id": "AC-INSIGHT-2",
                "framework": "Playwright",
                "language": "Python",
                "file_name": "test_second.py",
                "created_at": "2026-01-03T03:04:05+00:00",
                "code": "print('second artifact')",
            }
        ],
    }
    report_payload = {
        "total_executions": 3,
        "passed": 2,
        "failed": 1,
        "not_executed": 0,
        "error": 0,
        "pass_rate_percent": 66.7,
        "total_duration_seconds": 2.5,
        "average_duration_seconds": 0.83,
    }
    failures_payload = {
        "total_executions": 3,
        "failed_executions": 1,
        "error_executions": 0,
        "total_failures": 1,
        "failure_rate_percent": 33.3,
        "affected_automation_cases": ["AC-INSIGHT-1"],
        "latest_failure_execution_id": "EX-INSIGHT-1",
        "latest_failure_status": "FAILED",
        "failures": [
            {
                "execution_id": "EX-INSIGHT-1",
                "automation_artifact_id": "ART-INSIGHT-1",
                "automation_case_id": "AC-INSIGHT-1",
                "status": "FAILED",
                "exit_code": 1,
                "message": "Expected value was not found",
                "stderr": "",
                "duration_seconds": 0.8,
            }
        ],
    }
    generated_suite_payload = {
        "project": {"project_id": "insights-project", "name": "Insights Project"},
        "requirement_version": {"version_id": "REQ-NEW-1", "version": 3},
        "test_cases": {
            "test_cases": [
                {
                    "id": "TC-GENERATED-1",
                    "title": "Generated requirement check",
                    "priority": "High",
                    "test_type": "Functional",
                    "preconditions": [
                        '<script>window.generatedCaseRan=true;</script>'
                    ],
                    "steps": [
                        '<img src="x" onerror="window.generatedCaseRan=true">'
                    ],
                    "expected_result": (
                        '<svg onload="window.generatedCaseRan=true">'
                    ),
                }
            ]
        },
        "analysis": {"summary": "Requirement analyzed."},
        "review": {"overall_quality": "Good", "coverage_score": 90},
    }
    qa_suite_requests = []
    qa_suite_save_requests = []
    requests = []
    execution_requests = []
    browser_requests = []

    def fulfill_json(route, payload, status=200):
        route.fulfill(
            status=status,
            content_type="application/json",
            body=json.dumps(payload),
        )

    try:
        deadline = time.time() + 10
        while not server.started:
            if time.time() >= deadline:
                raise AssertionError(
                    "Uvicorn server did not start within 10 seconds"
                )
            time.sleep(0.05)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            console_errors = []
            page_errors = []
            page.on(
                "console",
                lambda message: console_errors.append(message.text)
                if message.type == "error"
                else None,
            )
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.on(
                "request",
                lambda request: browser_requests.append(
                    (request.method, request.url)
                ),
            )

            def handle_projects(route):
                requests.append(route.request.url)
                fulfill_json(
                    route,
                    [
                        {
                            "project_id": "insights-project",
                            "name": "Insights Project",
                            "application": "QA app",
                            "environment": "test",
                            "description": "",
                            "metadata": {},
                        }
                    ],
                )

            def handle_workspace(route):
                requests.append(route.request.url)
                fulfill_json(route, workspace_payload)

            def handle_qa_suite(route):
                qa_suite_requests.append(route.request.post_data_json)
                fulfill_json(route, generated_suite_payload)

            def handle_qa_suite_save(route):
                request_payload = route.request.post_data_json
                qa_suite_save_requests.append(request_payload)
                workspace_payload["test_cases"].append(
                    {
                        **generated_suite_payload["test_cases"]["test_cases"][0],
                        "automation_candidate": False,
                        "suite_id": "SUITE-NEW-1",
                        "suite_version": 3,
                        "requirement_version_id": "REQ-NEW-1",
                    }
                )
                fulfill_json(
                    route,
                    {"suite_id": "SUITE-NEW-1", "project_id": "insights-project", "version": 3},
                )

            def handle_history(route):
                requests.append(route.request.url)
                fulfill_json(
                    route,
                    [
                        {
                            "execution_id": "EX-INSIGHT-1",
                            "automation_artifact_id": "ART-INSIGHT-1",
                            "automation_case_id": "AC-INSIGHT-1",
                            "status": "FAILED",
                            "exit_code": 1,
                            "stdout": "",
                            "stderr": "Expected value was not found",
                            "duration_seconds": 0.8,
                            "error": None,
                        }
                    ],
                )

            def handle_report(route):
                requests.append(route.request.url)
                fulfill_json(route, report_payload)

            def handle_failures(route):
                requests.append(route.request.url)
                if failures_payload.get("api_error"):
                    fulfill_json(
                        route,
                        {"detail": "Project failure analysis unavailable"},
                        status=500,
                    )
                else:
                    fulfill_json(route, failures_payload)

            def handle_execution_detail(route):
                requests.append(route.request.url)
                fulfill_json(
                    route,
                    {
                        "execution_id": "EX-INSIGHT-1",
                        "automation_artifact_id": "ART-INSIGHT-1",
                        "automation_case_id": "AC-INSIGHT-1",
                        "status": "FAILED",
                        "exit_code": 1,
                        "stdout": "",
                        "stderr": "Expected value was not found",
                        "duration_seconds": 0.8,
                        "error": None,
                    },
                )

            def handle_artifact_execution(route):
                execution_requests.append(route.request.url)
                fulfill_json(
                    route,
                    {
                        "status": "PASSED",
                        "stdout": "Execution completed",
                        "stderr": "",
                    },
                )

            page.route("**/api/projects", handle_projects)
            page.route(
                "**/api/projects/insights-project/workspace",
                handle_workspace,
            )
            page.route(
                "**/api/projects/insights-project/qa-suite",
                handle_qa_suite,
            )
            page.route(
                "**/api/projects/insights-project/qa-suite/save",
                handle_qa_suite_save,
            )
            page.route(
                "**/api/projects/insights-project/executions?limit=50",
                handle_history,
            )
            page.route(
                "**/api/projects/insights-project/executions/report",
                handle_report,
            )
            page.route(
                "**/api/projects/insights-project/executions/failures*",
                handle_failures,
            )
            page.route(
                "**/api/projects/insights-project/executions/EX-INSIGHT-1",
                handle_execution_detail,
            )
            page.route(
                "**/api/projects/insights-project/automation/*/execute",
                handle_artifact_execution,
            )

            page.goto(
                "http://127.0.0.1:8766/project-workspace?project_id=insights-project",
                wait_until="networkidle",
            )

            expect(page.get_by_role("heading", name="Insights Project")).to_be_visible()
            expect(page.get_by_role("heading", name="Project Overview")).to_be_visible()
            expect(page.locator("#project-overview-execution-count")).to_have_text("3")
            expect(page.locator("#project-overview-passed")).to_have_text("2")
            expect(page.locator("#project-overview-failed")).to_have_text("1")
            expect(page.locator("#project-overview-pass-rate")).to_have_text("66.7%")
            expect(page.locator("#project-overview-activity")).to_contain_text(
                "Recent failure: Expected value was not found"
            )
            expect(page.get_by_role("button", name="Generate or review a QA suite")).to_be_visible()
            overview_tab = page.get_by_role("tab", name="Overview")
            overview_tab.focus()
            overview_tab.press("ArrowRight")
            expect(page.get_by_role("tab", name="Requirements")).to_have_attribute(
                "aria-selected",
                "true",
            )
            overview_tab.click()
            insights = page.locator(
                "#project-execution-insights"
            )
            page.get_by_role("tab", name="Reports").click()
            insights.get_by_text(
                "Expected value was not found"
            ).wait_for()

            page.get_by_role("tab", name="Test Cases").click()
            test_case_count = page.locator("#saved-test-case-count")
            expect(test_case_count).to_have_text("Showing 2 of 2 test cases")
            page.get_by_label("Search").fill("TC-INSIGHT-2")
            expect(test_case_count).to_have_text("Showing 1 of 2 test cases")
            expect(page.locator("[data-test-case-filter-row]:visible")).to_have_count(1)
            page.get_by_label("Search").fill("")
            page.get_by_label("Priority").select_option("Critical")
            expect(page.locator("[data-test-case-filter-row]:visible")).to_have_count(1)
            page.get_by_label("Priority").select_option("")

            # Saved-case review uses the exact selected workspace row and is
            # read-only. Its content is inserted as inert DOM text.
            test_case_table = page.locator(
                "#project-area-test-cases table"
            )
            expect(test_case_table).to_contain_text("Requirement Version")
            expect(test_case_table).to_contain_text("REQ-INSIGHT-1")
            expect(test_case_table).to_contain_text("REQ-INSIGHT-2")
            first_test_case_row = test_case_table.locator(
                "tbody tr"
            ).nth(0)
            second_test_case_row = test_case_table.locator(
                "tbody tr"
            ).nth(1)
            case_review_panel = page.locator(
                "#project-test-case-review"
            )
            requests_before_case_review = len(browser_requests)

            first_test_case_row.get_by_role(
                "button",
                name="Review test case TC-INSIGHT-1",
            ).click()
            expect(case_review_panel).to_be_visible()
            expect(case_review_panel).to_contain_text(
                "Saved Test Case Review"
            )
            expect(case_review_panel).to_contain_text(
                "User is signed in"
            )
            expect(case_review_panel).to_contain_text(
                "Account is active"
            )
            steps = case_review_panel.locator("ol li")
            expect(steps).to_have_count(2)
            expect(steps.nth(0)).to_have_text(
                "Open the sign-in page"
            )
            expect(steps.nth(1)).to_have_text(
                "Submit valid credentials"
            )
            expect(case_review_panel).to_contain_text(
                "Expected Result: Dashboard appears"
            )
            expect(case_review_panel).to_contain_text(
                "Priority: High"
            )
            expect(case_review_panel).to_contain_text(
                "Test Type: Functional"
            )
            expect(case_review_panel).to_contain_text(
                "Suite ID: SUITE-INSIGHT-1"
            )
            expect(case_review_panel).to_contain_text(
                "Suite Version: 1"
            )
            expect(case_review_panel).to_contain_text(
                "Requirement Version ID: REQ-INSIGHT-1"
            )

            second_test_case_row.get_by_role(
                "button",
                name="Review test case TC-INSIGHT-2",
            ).click()
            expect(case_review_panel).to_contain_text(
                "Requirement Version ID: REQ-INSIGHT-2"
            )
            expect(case_review_panel).to_contain_text(
                "Suite Version: 2"
            )
            expect(case_review_panel.locator("ul li").first).to_have_text(
                "<script>window.caseExecuted=true;</script>"
            )
            expect(steps.nth(0)).to_have_text(
                "<b>First hostile step</b>"
            )
            expect(steps.nth(1)).to_have_text(
                '<img src="x" onerror="window.caseStepRan=true">'
            )
            expect(case_review_panel).to_contain_text(
                '<svg onload="window.caseExpectedRan=true">'
            )
            assert case_review_panel.locator(
                "script, img, svg, b"
            ).count() == 0
            assert page.evaluate(
                "window.caseExecuted || window.caseStepRan || "
                "window.caseExpectedRan || window.caseTitleRan || false"
            ) is False

            case_review_panel.get_by_role(
                "button",
                name="Close Review",
            ).click()
            expect(case_review_panel).to_be_hidden()

            # Candidate selection still works independently of Review.
            candidate_checkbox = page.get_by_role(
                "checkbox",
                name="Select Reviewable case",
            )
            candidate_checkbox.check()
            page.get_by_role("tab", name="Automation").click()
            expect(page.get_by_role(
                "button",
                name="Generate Automation (1 Selected)",
            )).to_be_visible()
            page.get_by_role("tab", name="Test Cases").click()
            candidate_checkbox.uncheck()
            page.get_by_role("tab", name="Automation").click()
            expect(page.get_by_role(
                "button",
                name="Generate Automation for Selected Candidates",
            )).to_be_visible()
            assert len(browser_requests) == requests_before_case_review

            # Reviewing generated source is read-only and treats markup-like
            # source as text. It must not call the execution endpoint.
            page.get_by_role("tab", name="Automation").click()
            review_panel = page.locator("#project-artifact-review")
            artifact_row = page.locator(
                "#project-workspace-result table"
            ).locator("tr").filter(has_text="ART-INSIGHT-1")
            artifact_row.get_by_role("button", name="Review").click()
            expect(review_panel).to_be_visible()
            expect(review_panel).to_contain_text("test_reviewable.py")
            expect(review_panel).to_contain_text("Playwright")
            expect(review_panel).to_contain_text("Python")
            expect(review_panel).to_contain_text("Created:")
            expect(review_panel).to_contain_text("Insights Project")
            expect(review_panel).to_contain_text(
                "TC-INSIGHT-1 — Reviewable case"
            )
            expect(review_panel).to_contain_text("AC-INSIGHT-1")
            expect(review_panel.locator("pre")).to_contain_text(
                "<script>window.artifactExecuted = true;</script>"
            )
            assert review_panel.locator("script").count() == 0
            assert page.evaluate(
                "window.artifactExecuted === true"
            ) is False
            assert not any(
                url.endswith("/automation/ART-INSIGHT-1/execute")
                for url in requests
            )

            second_row = page.locator(
                "#project-workspace-result table"
            ).locator("tr").filter(has_text="ART-INSIGHT-2")
            second_row.get_by_role("button", name="Review").click()
            expect(review_panel).to_contain_text("test_second.py")
            expect(review_panel.locator("pre")).to_have_text(
                "print('second artifact')"
            )
            expect(review_panel).not_to_contain_text("test_reviewable.py")
            review_panel.get_by_role(
                "button", name="Close Review"
            ).click()
            expect(review_panel).to_be_hidden()
            assert not any(
                "/automation/" in url and url.endswith("/execute")
                for url in requests
            )

            # Execute remains a distinct action and still calls the existing
            # project-scoped execution endpoint.
            artifact_row.get_by_role("button", name="Execute").click()
            page.get_by_text(
                "Execution result for ART-INSIGHT-1: PASSED"
            ).wait_for()
            assert execution_requests == [
                "http://127.0.0.1:8766/api/projects/insights-project/automation/ART-INSIGHT-1/execute"
            ]

            second_row.get_by_role(
                "button",
                name="Execute",
            ).click()
            page.get_by_text(
                "Execution result for ART-INSIGHT-2: PASSED"
            ).wait_for()
            assert execution_requests == [
                "http://127.0.0.1:8766/api/projects/insights-project/automation/ART-INSIGHT-1/execute",
                "http://127.0.0.1:8766/api/projects/insights-project/automation/ART-INSIGHT-2/execute",
            ]

            page.get_by_role("tab", name="Reports").click()
            assert insights.get_by_text("3", exact=True).first.is_visible()
            assert insights.locator(
                "#project-insights-passed"
            ).inner_text().strip() == "2"
            assert insights.locator(
                "#project-insights-failed"
            ).inner_text().strip() == "1"
            assert insights.locator(
                "#project-insights-errors"
            ).inner_text().strip() == "0"
            assert insights.get_by_text("66.7%", exact=True).is_visible()
            assert insights.get_by_text("EX-INSIGHT-1").is_visible()
            assert insights.get_by_text("AC-INSIGHT-1").is_visible()

            assert page.locator(
                '#project-execution-insights button[onclick*="openProjectExecutionReview"]'
            ).is_visible()
            insights.get_by_role(
                "button",
                name="Review",
            ).click()
            page.locator(
                "#project-execution-review"
            ).get_by_text("EX-INSIGHT-1").wait_for()

            assert any(
                "/api/projects/insights-project/executions/report"
                in url
                for url in requests
            )
            assert any(
                url.endswith("/api/projects/insights-project/workspace")
                for url in requests
            )
            assert any(
                "/api/projects/insights-project/executions/failures?limit=10"
                in url
                for url in requests
            )
            assert not any(
                url.endswith("/api/executions/report")
                or "/api/executions/failures" in url
                for url in requests
            )

            # No executions is an empty state, not an API error.
            report_payload.update(
                total_executions=0,
                passed=0,
                failed=0,
                error=0,
                pass_rate_percent=0.0,
            )
            failures_payload.update(
                total_executions=0,
                failed_executions=0,
                error_executions=0,
                total_failures=0,
                failure_rate_percent=0.0,
                failures=[],
            )
            page.get_by_role(
                "button",
                name="Load Project Workspace",
            ).click()
            page.get_by_role("tab", name="Reports").click()
            expect(
                insights.locator("#project-insights-total")
            ).to_have_text("0")
            insights.get_by_text(
                "No executions have been recorded for this project yet."
            ).wait_for()
            insights.get_by_text(
                "No failures recorded for this project."
            ).wait_for()

            # Project Requirements reuses the existing generate and save APIs.
            page.get_by_role("tab", name="Overview").click()
            page.get_by_role("button", name="Generate or review a QA suite").click()
            expect(page.get_by_role("tab", name="Requirements")).to_have_attribute(
                "aria-selected", "true"
            )
            page.locator("#project-qa-requirement").fill(
                "An authenticated user can complete the requirement flow."
            )
            page.get_by_role("button", name="Generate QA Suite").click()
            expect(page.get_by_role("heading", name="Generated QA Suite")).to_be_visible()
            expect(page.locator("#project-qa-generation-result")).to_contain_text(
                "Generated requirement check"
            )
            generated_review = page.locator(
                "#generated-project-test-case-review"
            )
            page.locator(
                "#generated-project-test-cases [data-generated-case-review]"
            ).click()
            expect(generated_review).to_be_visible()
            expect(generated_review.locator("ul li")).to_have_text(
                "<script>window.generatedCaseRan=true;</script>"
            )
            expect(generated_review.locator("ol li")).to_have_text(
                '<img src="x" onerror="window.generatedCaseRan=true">'
            )
            expect(generated_review).to_contain_text(
                '<svg onload="window.generatedCaseRan=true">'
            )
            assert generated_review.locator("script, img, svg").count() == 0
            assert page.evaluate("window.generatedCaseRan || false") is False
            generated_review.get_by_role(
                "button", name="Close Review"
            ).click()
            expect(generated_review).to_be_hidden()

            generated_case_checkbox = page.get_by_role(
                "checkbox", name="Select generated test case TC-GENERATED-1"
            )
            generated_case_checkbox.uncheck()
            page.get_by_role("button", name="Save Selected Test Cases").click()
            expect(page.locator("#project-qa-save-error")).to_have_text(
                "Select at least one test case to save."
            )
            assert qa_suite_save_requests == []
            generated_case_checkbox.check()
            page.get_by_role("button", name="Select All").click()
            expect(page.locator("#generated-project-test-case-count")).to_have_text(
                "Selected 1 of 1 test cases"
            )
            page.get_by_role("button", name="Clear All").click()
            expect(page.locator("#generated-project-test-case-count")).to_have_text(
                "Selected 0 of 1 test cases"
            )
            generated_case_checkbox.check()
            page.get_by_role("button", name="Save Selected Test Cases").click()
            expect(page.locator("#project-workspace-notice")).to_have_text(
                "Saved 1 test case."
            )
            expect(page.get_by_role("tab", name="Test Cases")).to_have_attribute(
                "aria-selected", "true"
            )
            expect(page.locator("#project-area-test-cases table")).to_contain_text(
                "TC-GENERATED-1"
            )
            assert qa_suite_requests == [
                {"requirement": "An authenticated user can complete the requirement flow."}
            ]
            assert qa_suite_save_requests[0]["requirement_version_id"] == "REQ-NEW-1"
            assert qa_suite_save_requests[0]["selected_test_case_ids"] == [
                "TC-GENERATED-1"
            ]

            # A project with executions and no failures is healthy.
            report_payload.update(
                total_executions=1,
                passed=1,
                pass_rate_percent=100.0,
            )
            failures_payload.update(
                total_executions=1,
                total_failures=0,
                failures=[],
            )
            page.get_by_role(
                "button",
                name="Load Project Workspace",
            ).click()
            page.get_by_role("tab", name="Reports").click()
            expect(
                insights.locator("#project-insights-total")
            ).to_have_text("1")
            insights.get_by_text(
                "No failures recorded for this project."
            ).wait_for()
            assert insights.get_by_text(
                "No executions have been recorded for this project yet."
            ).count() == 0

            # An API error is shown as an error, with no global fallback.
            failures_payload["api_error"] = True
            page.get_by_role(
                "button",
                name="Load Project Workspace",
            ).click()
            page.get_by_role("tab", name="Reports").click()
            insights.get_by_text(
                "Project failure analysis unavailable"
            ).wait_for()

            # Existing workspace and automation controls remain available.
            page.get_by_role("tab", name="Test Cases").click()
            assert page.get_by_text("Reviewable case").is_visible()
            assert page.get_by_role(
                "checkbox",
                name="Select Reviewable case",
            ).is_visible()
            page.get_by_role("tab", name="Automation").click()
            assert page.get_by_role(
                "button",
                name="Generate Automation for Selected Candidates",
            ).is_visible()
            assert page.get_by_role(
                "button",
                name="Execute",
            ).count() == 2

            # Empty artifact lists preserve the workspace and simply render
            # an empty artifact table with no review or execute actions.
            workspace_payload["automation_artifacts"] = []
            workspace_payload["test_cases"] = []
            page.get_by_role(
                "button",
                name="Load Project Workspace",
            ).click()
            page.get_by_role("tab", name="Automation").click()
            artifact_table = page.locator(
                "#project-area-automation table"
            )
            expect(artifact_table.locator("tbody tr")).to_have_count(1)
            expect(artifact_table).to_contain_text(
                "No automation artifacts have been generated for this project."
            )
            assert artifact_table.get_by_role(
                "button",
                name="Review",
            ).count() == 0
            expect(test_case_table.locator("tbody tr")).to_have_count(1)
            expect(test_case_table).to_contain_text(
                "No saved test cases are available for this project."
            )
            assert test_case_table.get_by_role(
                "button",
                name="Review",
            ).count() == 0
            expect(page.get_by_role(
                "button",
                name="Generate Automation for Selected Candidates",
            )).to_be_disabled()

            page.locator("#repository-project-id").select_option("")
            expect(
                page.get_by_role("heading", name="Insights Project")
            ).to_have_count(0)
            expect(page.locator("#project-area-executions")).to_be_hidden()
            expect(
                page.locator("#project-workspace-action")
            ).to_be_hidden()

            page.set_viewport_size({"width": 390, "height": 844})
            assert page.evaluate(
                "document.documentElement.scrollWidth <= window.innerWidth"
            ) is True
            assert all(
                "Failed to load resource" in message
                for message in console_errors
            )
            assert page_errors == []

            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        if thread.is_alive():
            raise AssertionError(
                "Uvicorn server did not shut down cleanly"
            )
