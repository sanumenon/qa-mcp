from __future__ import annotations

import os
import sqlite3
import stat
import time
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from qa_mcp.core.project.context import ProjectContext
from qa_mcp.core.security.actor import (
    LOCAL_OPERATOR,
    Actor,
    reset_current_actor,
    set_current_actor,
)
from qa_mcp.core.security.authorization import AuthorizationError, ProjectAuthorization
from qa_mcp.core.security.backup import create_database_backup, restore_database_backup
from qa_mcp.core.security.oidc import GoogleOIDCProvider
from qa_mcp.core.versioning.service import QASuiteVersioningService
from qa_mcp.infrastructure.sqlite_authorization_repository import SQLiteAuthorizationRepository
from qa_mcp.infrastructure.sqlite_project_repository import SQLiteProjectRepository
from qa_mcp.infrastructure.sqlite_automation_execution_repository import SQLiteAutomationExecutionRepository
from qa_mcp.infrastructure.sqlite_qa_workspace_artifact_repository import SQLiteQAWorkspaceArtifactRepository
from qa_mcp.infrastructure.versioning.sqlite_version_repository import (
    SQLiteRequirementVersionRepository,
    SQLiteSuiteVersionRepository,
)
from qa_mcp.models.schemas import (
    AutomationExecutionResult,
    GeneratedAutomationArtifact,
    QAProject,
    TestCaseResponse,
    TestCaseReview as Review,
)
from qa_mcp.web.auth import install_authentication_middleware


def _project(project_id: str) -> QAProject:
    return QAProject(
        project_id=project_id,
        name=project_id,
        description="",
        application="app",
        environment="qa",
        metadata={},
    )


def test_transactional_migration_preserves_existing_records_and_maps_only_explicit_owner(tmp_path):
    database = tmp_path / "existing.sqlite3"
    projects = SQLiteProjectRepository(str(database))
    projects.create(_project("legacy-a"))
    projects.create(_project("legacy-unmapped"))
    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE qa_requirement_versions (version_id TEXT PRIMARY KEY, payload TEXT)"
        )
        connection.execute(
            "INSERT INTO qa_requirement_versions VALUES ('req-existing', 'keep')"
        )
        connection.execute(
            "CREATE TABLE qa_workspace_automation_artifacts (artifact_id TEXT PRIMARY KEY, code TEXT)"
        )
        connection.execute(
            "INSERT INTO qa_workspace_automation_artifacts VALUES ('artifact-existing', 'keep')"
        )
        connection.execute(
            "CREATE TABLE automation_execution_history (execution_id TEXT PRIMARY KEY, stdout TEXT)"
        )
        connection.execute(
            "INSERT INTO automation_execution_history VALUES ('execution-existing', 'keep')"
        )

    auth_repository = SQLiteAuthorizationRepository(
        str(database), {"legacy-a": "google-subject-a"}
    )
    assert auth_repository.migration_version() == 1
    assert auth_repository.is_project_member("legacy-a", "google-subject-a")
    assert auth_repository.unmapped_project_ids() == ["legacy-unmapped"]
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT payload FROM qa_requirement_versions").fetchone() == ("keep",)
        assert connection.execute("SELECT code FROM qa_workspace_automation_artifacts").fetchone() == ("keep",)
        assert connection.execute("SELECT stdout FROM automation_execution_history").fetchone() == ("keep",)

    authorization = ProjectAuthorization(auth_repository)
    actor_token = set_current_actor(Actor("google-subject-a"))
    try:
        authorization.require_project("legacy-a")
        with pytest.raises(AuthorizationError):
            authorization.require_project("legacy-unmapped")
    finally:
        reset_current_actor(actor_token)


def test_project_membership_isolation_and_creator_membership(tmp_path):
    database = str(tmp_path / "qa.sqlite3")
    projects = SQLiteProjectRepository(database)
    projects.create(_project("project-a"))
    projects.create(_project("project-b"))
    repository = SQLiteAuthorizationRepository(database)
    repository.grant_project_member("project-a", "user-a")
    repository.grant_project_member("project-b", "user-b")
    authorization = ProjectAuthorization(repository, ["admin-subject"])
    context = ProjectContext(projects, authorization)

    token = set_current_actor(Actor("user-a"))
    try:
        assert [item.project_id for item in context.list_projects()] == ["project-a"]
        context.get_project("project-a")
        with pytest.raises(AuthorizationError):
            context.get_project("project-b")
        with pytest.raises(AuthorizationError):
            authorization.require_project("project-b")
    finally:
        reset_current_actor(token)

    token = set_current_actor(Actor("user-b"))
    try:
        assert [item.project_id for item in context.list_projects()] == ["project-b"]
        with pytest.raises(AuthorizationError):
            context.get_project("project-a")
    finally:
        reset_current_actor(token)

    token = set_current_actor(Actor("new-creator"))
    try:
        context.create_project(_project("project-c"))
        assert repository.is_project_member("project-c", "new-creator")
    finally:
        reset_current_actor(token)

    token = set_current_actor(Actor("admin-subject"))
    try:
        assert len(context.list_projects()) == 3
    finally:
        reset_current_actor(token)


def test_suite_version_rejects_cross_project_requirement_version(tmp_path):
    database = str(tmp_path / "qa.sqlite3")
    projects = SQLiteProjectRepository(database)
    projects.create(_project("project-a"))
    projects.create(_project("project-b"))
    auth_repository = SQLiteAuthorizationRepository(database)
    auth_repository.grant_project_member("project-a", "actor-a")
    authorization = ProjectAuthorization(auth_repository)
    requirement_repository = SQLiteRequirementVersionRepository(database)
    suite_repository = SQLiteSuiteVersionRepository(database)
    from qa_mcp.core.versioning.service import QARequirementVersioningService

    requirements = QARequirementVersioningService(requirement_repository)
    req_a = requirements.create_requirement_version("project-a", "A", "app", "qa")
    req_b = requirements.create_requirement_version("project-b", "B", "app", "qa")
    suites = QASuiteVersioningService(
        suite_repository,
        requirement_repository=requirement_repository,
        authorization=authorization,
    )
    cases = TestCaseResponse.model_validate({"test_cases": []})
    review = Review.model_validate(
        {
            "overall_quality": "Good", "coverage_score": 80,
            "duplicate_test_cases": [], "missing_scenarios": [],
            "weak_test_cases": [], "requirement_gaps": [],
            "priority_issues": [], "recommendations": [], "summary": "ok",
        }
    )
    token = set_current_actor(Actor("actor-a"))
    try:
        assert suites.create_suite_version("project-a", req_a.version_id, cases, review)
        with pytest.raises(ValueError, match="different project"):
            suites.create_suite_version("project-a", req_b.version_id, cases, review)
        with pytest.raises(AuthorizationError):
            suites.create_suite_version("project-b", req_b.version_id, cases, review)
    finally:
        reset_current_actor(token)


def test_oidc_provider_accepts_only_verified_workspace_claims():
    settings = {
        "google_client_id": "client-id",
        "google_client_secret": "not-a-real-secret",
        "redirect_uri": "https://qa.example.test/auth/callback",
        "workspace_domain": "qa.example.test",
    }
    provider = object.__new__(GoogleOIDCProvider)
    provider.settings = settings

    class VerifiedGoogleClient:
        claims = {
            "sub": "stable-google-subject",
            "email": "qa-user@qa.example.test",
            "email_verified": True,
            "hd": "qa.example.test",
        }

        async def authorize_access_token(self, request):
            return {"userinfo": dict(self.claims), "access_token": "must-not-persist"}

    provider.oauth = cast(
        Any,
        SimpleNamespace(google=VerifiedGoogleClient()),
    )
    actor = __import__("asyncio").run(provider.complete(object()))
    assert actor.subject == "stable-google-subject"
    assert actor.email == "qa-user@qa.example.test"
    assert actor.authenticated

    provider.oauth.google.claims = {
        "sub": "outside-subject", "email": "outside@example.net",
        "email_verified": True, "hd": "example.net",
    }
    with pytest.raises(ValueError, match="Workspace domain"):
        __import__("asyncio").run(provider.complete(object()))

    provider.oauth.google.claims = {
        "sub": "unverified", "email": "qa-user@qa.example.test",
        "email_verified": False, "hd": "qa.example.test",
    }
    with pytest.raises(ValueError, match="not verified"):
        __import__("asyncio").run(provider.complete(object()))


def test_google_session_authentication_csrf_and_logout(monkeypatch):
    import qa_mcp.web.app as web_app

    from qa_mcp.core.security.actor import Actor

    class FakeOIDC:
        async def complete(self, request):
            return Actor("google-subject-123", "member@example.test")

    monkeypatch.setitem(web_app.auth_settings, "mode", "google")
    monkeypatch.setattr(web_app, "oidc_provider", FakeOIDC())
    try:
        client = TestClient(web_app.app)
        assert client.get("/api/auth/me").status_code == 401
        browser_unauthenticated = client.get("/", follow_redirects=False)
        assert browser_unauthenticated.status_code == 401
        assert "/auth/login" in browser_unauthenticated.text
        callback = client.get("/auth/callback", follow_redirects=False)
        assert callback.status_code == 303
        identity = client.get("/api/auth/me")
        assert identity.status_code == 200
        assert identity.json()["subject"] == "google-subject-123"
        assert identity.json()["email"] == "member@example.test"
        assert "access_token" not in identity.json()
        assert "id_token" not in identity.json()
        assert any(
            "qa_session=" in cookie and "httponly" in cookie.lower()
            for cookie in callback.headers.get_list("set-cookie")
        )
        assert client.post("/auth/logout").status_code == 403
        csrf = client.cookies.get("qa_csrf")
        assert csrf
        assert client.post(
            "/auth/logout", headers={"X-CSRF-Token": csrf}
        ).status_code == 200
        assert client.get("/api/auth/me").status_code == 401
    finally:
        monkeypatch.setitem(web_app.auth_settings, "mode", "development")


def test_authenticated_web_users_are_isolated_between_projects(monkeypatch, tmp_path):
    import qa_mcp.web.app as web_app

    repo = SQLiteProjectRepository(str(tmp_path / "api.sqlite3"))
    repo.create(_project("api-project-a"))
    repo.create(_project("api-project-b"))
    auth_repo = SQLiteAuthorizationRepository(str(tmp_path / "api.sqlite3"))
    auth_repo.grant_project_member("api-project-a", "google-user-a")
    auth_repo.grant_project_member("api-project-b", "google-user-b")
    authorization = ProjectAuthorization(auth_repo)
    context = ProjectContext(repo, authorization)

    class WorkspaceStub:
        def get_project_qa_workspace(self, project_id):
            project = context.get_project(project_id)
            return {"project": project.model_dump()}

    class FakeOIDC:
        def __init__(self):
            self.subjects = iter(("google-user-a", "google-user-b"))

        async def complete(self, request):
            subject = next(self.subjects)
            return Actor(subject, f"{subject}@example.test")

    monkeypatch.setitem(web_app.auth_settings, "mode", "google")
    monkeypatch.setattr(web_app, "oidc_provider", FakeOIDC())
    monkeypatch.setattr(web_app, "qa_workspace_service", WorkspaceStub())
    monkeypatch.setattr(web_app.authorization_repository, "record_audit", lambda *args: None)
    try:
        client_a = TestClient(web_app.app)
        client_b = TestClient(web_app.app)
        assert client_a.get("/auth/callback", follow_redirects=False).status_code == 303
        assert client_b.get("/auth/callback", follow_redirects=False).status_code == 303
        assert client_a.get("/api/projects/api-project-a/workspace").status_code == 200
        assert client_a.get("/api/projects/api-project-b/workspace").status_code == 403
        assert client_b.get("/api/projects/api-project-b/workspace").status_code == 200
        assert client_b.get("/api/projects/api-project-a/workspace").status_code == 403
    finally:
        monkeypatch.setitem(web_app.auth_settings, "mode", "development")


def test_mcp_suite_tool_enforces_project_and_requirement_scope(monkeypatch, tmp_path):
    import qa_mcp.server as server

    database = str(tmp_path / "mcp.sqlite3")
    projects = SQLiteProjectRepository(database)
    projects.create(_project("mcp-project-a"))
    projects.create(_project("mcp-project-b"))
    auth_repo = SQLiteAuthorizationRepository(database)
    auth_repo.grant_project_member("mcp-project-a", "mcp-user-a")
    authorization = ProjectAuthorization(auth_repo)
    requirement_repo = SQLiteRequirementVersionRepository(database)
    suite_repo = SQLiteSuiteVersionRepository(database)
    from qa_mcp.core.versioning.service import QARequirementVersioningService

    requirements = QARequirementVersioningService(requirement_repo)
    req_a = requirements.create_requirement_version("mcp-project-a", "A", "app", "qa")
    req_b = requirements.create_requirement_version("mcp-project-b", "B", "app", "qa")
    service = QASuiteVersioningService(
        suite_repo, requirement_repo, authorization
    )
    monkeypatch.setattr(server, "suite_versioning_service", service)
    cases = {"test_cases": []}
    review = {
        "overall_quality": "Good", "coverage_score": 80,
        "duplicate_test_cases": [], "missing_scenarios": [],
        "weak_test_cases": [], "requirement_gaps": [],
        "priority_issues": [], "recommendations": [], "summary": "ok",
    }
    token = set_current_actor(Actor("mcp-user-a"))
    try:
        with pytest.raises(ValueError, match="different project"):
            server.create_suite_version("mcp-project-a", req_b.version_id, cases, review)
        with pytest.raises(AuthorizationError):
            server.create_suite_version("mcp-project-b", req_b.version_id, cases, review)
        allowed = server.create_suite_version("mcp-project-a", req_a.version_id, cases, review)
        assert allowed["project_id"] == "mcp-project-a"
    finally:
        reset_current_actor(token)


def test_web_suite_save_rejects_cross_project_requirement_version(monkeypatch, tmp_path):
    import qa_mcp.web.app as web_app
    from qa_mcp.core.versioning.service import QARequirementVersioningService

    database = str(tmp_path / "web-version.sqlite3")
    project_repository = SQLiteProjectRepository(database)
    project_repository.create(_project("web-project-a"))
    project_repository.create(_project("web-project-b"))
    auth_repository = SQLiteAuthorizationRepository(database)
    auth_repository.grant_project_member("web-project-a", "api-user-a")
    authorization = ProjectAuthorization(auth_repository)
    requirement_repository = SQLiteRequirementVersionRepository(database)
    suite_repository = SQLiteSuiteVersionRepository(database)
    requirement_service = QARequirementVersioningService(requirement_repository)
    requirement_a = requirement_service.create_requirement_version(
        "web-project-a", "A", "app", "qa"
    )
    requirement_b = requirement_service.create_requirement_version(
        "web-project-b", "B", "app", "qa"
    )
    suite_service = QASuiteVersioningService(
        suite_repository, requirement_repository, authorization
    )

    class WorkspaceFacade:
        def save_selected_test_cases(self, **kwargs):
            return suite_service.create_suite_version(
                project_id=kwargs["project_id"],
                requirement_version_id=kwargs["requirement_version_id"],
                test_cases=TestCaseResponse.model_validate(kwargs["test_cases"]),
                review=Review.model_validate(kwargs["review"]),
            ).model_dump()

    monkeypatch.setattr(web_app, "qa_workspace_service", WorkspaceFacade())
    monkeypatch.setitem(web_app.auth_settings, "development_subject", "api-user-a")
    try:
        client = TestClient(web_app.app)
        request_payload = {
            "requirement_version_id": requirement_b.version_id,
            "test_cases": {"test_cases": []},
            "review": {
                "overall_quality": "Good", "coverage_score": 80,
                "duplicate_test_cases": [], "missing_scenarios": [],
                "weak_test_cases": [], "requirement_gaps": [],
                "priority_issues": [], "recommendations": [], "summary": "ok",
            },
            "selected_test_case_ids": ["TC-any"],
        }
        cross_version = client.post(
            "/api/projects/web-project-a/qa-suite/save", json=request_payload
        )
        assert cross_version.status_code == 400
        assert "different project" in cross_version.json()["detail"]
        denied_project = client.post(
            "/api/projects/web-project-b/qa-suite/save", json=request_payload
        )
        assert denied_project.status_code == 403
    finally:
        monkeypatch.setitem(web_app.auth_settings, "development_subject", "local-development")


def test_global_execution_apis_filter_to_actor_projects(monkeypatch, tmp_path):
    import qa_mcp.web.app as web_app
    from qa_mcp.core.automation.execution_failure_analysis_service import AutomationExecutionFailureAnalysisService
    from qa_mcp.core.automation.execution_history_service import AutomationExecutionHistoryService
    from qa_mcp.core.automation.execution_reporting_service import AutomationExecutionReportingService

    database = str(tmp_path / "global-executions.sqlite3")
    projects = SQLiteProjectRepository(database)
    projects.create(_project("global-a"))
    projects.create(_project("global-b"))
    auth_repository = SQLiteAuthorizationRepository(database)
    auth_repository.grant_project_member("global-a", "api-user-a")
    auth_repository.grant_project_member("global-b", "api-user-b")
    authorization = ProjectAuthorization(auth_repository)
    artifact_repository = SQLiteQAWorkspaceArtifactRepository(database)
    history_repository = SQLiteAutomationExecutionRepository(database)
    for suffix, project_id in (("a", "global-a"), ("b", "global-b")):
        artifact = GeneratedAutomationArtifact(
            id=f"artifact-{suffix}", automation_case_id=f"case-{suffix}",
            framework="Playwright", language="Python", file_name=f"test_{suffix}.py", code="pass",
        )
        artifact_repository.save(artifact, project_id, f"testcase-{suffix}", "2026-01-01T00:00:00Z")
        history_repository.save(
            AutomationExecutionResult(
                execution_id=f"execution-{suffix}",
                automation_artifact_id=artifact.id,
                automation_case_id=artifact.automation_case_id,
                status="FAILED" if suffix == "a" else "PASSED",
                exit_code=1 if suffix == "a" else 0,
                stderr="private A output" if suffix == "a" else "",
            )
        )

    history = AutomationExecutionHistoryService(history_repository)
    monkeypatch.setattr(web_app, "project_authorization", authorization)
    monkeypatch.setattr(web_app, "workspace_artifact_repository", artifact_repository)
    monkeypatch.setattr(web_app, "history_service", history)
    monkeypatch.setattr(web_app, "reporting_service", AutomationExecutionReportingService(history))
    monkeypatch.setattr(
        web_app, "failure_analysis_service",
        AutomationExecutionFailureAnalysisService(history_repository),
    )
    monkeypatch.setitem(web_app.auth_settings, "development_subject", "api-user-a")
    try:
        client = TestClient(web_app.app)
        executions = client.get("/api/executions").json()
        report = client.get("/api/executions/report").json()
        failures = client.get("/api/executions/failures").json()
        assert [item["execution_id"] for item in executions] == ["execution-a"]
        assert report["total_executions"] == 1
        assert failures["total_executions"] == 1
        assert failures["failures"][0]["execution_id"] == "execution-a"
        assert "execution-b" not in str(failures)
    finally:
        monkeypatch.setitem(web_app.auth_settings, "development_subject", "local-development")


def test_readiness_reports_database_and_legacy_mapping_state(monkeypatch):
    import qa_mcp.web.app as web_app

    monkeypatch.setattr(web_app.authorization_repository, "database_ready", lambda: False)
    monkeypatch.setattr(web_app.authorization_repository, "unmapped_project_ids", lambda: [])
    response = TestClient(web_app.app).get("/api/ready")
    assert response.status_code == 503
    assert response.json()["checks"]["database"] == "unavailable"


def test_only_global_admin_can_manage_project_members(monkeypatch, tmp_path):
    import qa_mcp.web.app as web_app

    database = str(tmp_path / "member-api.sqlite3")
    projects = SQLiteProjectRepository(database)
    projects.create(_project("member-api-project"))
    auth_repository = SQLiteAuthorizationRepository(database)
    authorization = ProjectAuthorization(auth_repository, ["configured-admin"])
    monkeypatch.setattr(web_app, "project_authorization", authorization)
    monkeypatch.setattr(web_app, "authorization_repository", auth_repository)
    monkeypatch.setitem(web_app.auth_settings, "development_subject", "configured-admin")
    try:
        client = TestClient(web_app.app)
        added = client.post(
            "/api/projects/member-api-project/members",
            json={"actor_id": "google-subject-member"},
        )
        assert added.status_code == 200
        assert auth_repository.is_project_member(
            "member-api-project", "google-subject-member"
        )
        removed = client.delete(
            "/api/projects/member-api-project/members/google-subject-member"
        )
        assert removed.status_code == 200
        assert not auth_repository.is_project_member(
            "member-api-project", "google-subject-member"
        )
    finally:
        monkeypatch.setitem(web_app.auth_settings, "development_subject", "local-development")


def test_browser_google_session_identity_access_denied_and_expiry(monkeypatch):
    import threading
    import time as time_module

    import uvicorn
    from playwright.sync_api import expect, sync_playwright

    import qa_mcp.web.app as web_app

    class FakeOIDC:
        async def complete(self, request):
            return Actor("browser-google-sub", "workspace-verified@example.test")

    class DeniedWorkspace:
        def get_project_qa_workspace(self, project_id):
            raise AuthorizationError("Project access denied")

    monkeypatch.setitem(web_app.auth_settings, "mode", "google")
    monkeypatch.setattr(web_app, "oidc_provider", FakeOIDC())
    monkeypatch.setattr(web_app, "qa_workspace_service", DeniedWorkspace())
    monkeypatch.setattr(web_app.authorization_repository, "record_audit", lambda *args: None)
    server = uvicorn.Server(
        uvicorn.Config(
            web_app.app,
            host="127.0.0.1",
            port=8767,
            log_level="error",
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        deadline = time_module.time() + 10
        while not server.started:
            if time_module.time() >= deadline:
                raise AssertionError("Authentication browser server did not start")
            time_module.sleep(0.05)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto("http://127.0.0.1:8767/")
            expect(page.get_by_role("heading", name="Sign in required")).to_be_visible()
            page.goto("http://127.0.0.1:8767/auth/callback")
            expect(page.locator(".auth-identity")).to_contain_text(
                "workspace-verified@example.test"
            )
            denied = page.evaluate(
                "async () => (await fetch('/api/projects/denied-project/workspace')).status"
            )
            assert denied == 403
            expect(page.locator("#qa-access-denied")).to_contain_text(
                "do not have access"
            )
            context.clear_cookies()
            page.goto("http://127.0.0.1:8767/")
            expect(page.get_by_role("heading", name="Sign in required")).to_be_visible()
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        monkeypatch.setitem(web_app.auth_settings, "mode", "development")


def test_expired_session_fails_closed():
    from qa_mcp.web.auth import AuthenticationMiddleware

    middleware = object.__new__(AuthenticationMiddleware)
    middleware.settings = {"mode": "google"}

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
            "query_string": b"",
            "scheme": "http",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
            "root_path": "",
            "session": {
                "actor_sub": "subject",
                "actor_email": "x@example.test",
                "expires_at": time.time() - 1,
            },
        }
    )

    assert middleware._session_actor(request) is None
@pytest.mark.parametrize(
    "settings,match",
    [
        ({"mode": "development", "environment": "production"}, "requires Google"),
        ({"mode": "google", "environment": "production"}, "incomplete"),
    ],
)
def test_auth_configuration_fails_closed_in_production(tmp_path, settings, match):
    app = FastAPI()
    projects = SQLiteProjectRepository(str(tmp_path / "db.sqlite3"))
    repo = SQLiteAuthorizationRepository(str(tmp_path / "db.sqlite3"))
    with pytest.raises(RuntimeError, match=match):
        install_authentication_middleware(
            app, settings, ProjectAuthorization(repo), repo
        )


def test_production_oidc_requires_configured_global_admin(tmp_path):
    settings = {
        "mode": "google",
        "environment": "production",
        "google_client_id": "client-id",
        "google_client_secret": "client-secret",
        "redirect_uri": "https://qa.example.test/auth/callback",
        "workspace_domain": "qa.example.test",
        "session_secret": "s" * 40,
        "session_max_age_seconds": 3600,
        "cookie_secure": True,
        "global_admin_subjects": [],
    }
    app = FastAPI()
    projects = SQLiteProjectRepository(str(tmp_path / "admin-required.sqlite3"))
    repo = SQLiteAuthorizationRepository(str(tmp_path / "admin-required.sqlite3"))
    with pytest.raises(RuntimeError, match="global administrator"):
        install_authentication_middleware(
            app, settings, ProjectAuthorization(repo), repo
        )


def test_online_backup_restore_integrity_retention_and_permissions(tmp_path):
    database = tmp_path / "qa.sqlite3"
    projects = SQLiteProjectRepository(str(database))
    projects.create(_project("restore-me"))
    backups = tmp_path / "backups"
    first = create_database_backup(database, backups, retention=2)
    projects.create(_project("also-backup"))
    second = create_database_backup(database, backups, retention=2)
    projects.create(_project("latest"))
    third = create_database_backup(database, backups, retention=2)

    assert not first.exists()  # the configured retention prunes the oldest copy
    assert second.exists() and third.exists()
    assert len(list(backups.glob("qa_mcp-*.sqlite3"))) == 2
    assert stat.S_IMODE(backups.stat().st_mode) == 0o700
    assert stat.S_IMODE(third.stat().st_mode) == 0o600
    with sqlite3.connect(third) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)

    restored = tmp_path / "restore" / "restored.sqlite3"
    restore_database_backup(third, restored)
    restored_projects = SQLiteProjectRepository(str(restored))
    assert restored_projects.exists("restore-me")
    assert restored_projects.exists("also-backup")
    assert restored_projects.exists("latest")

def test_development_local_operator_uses_trusted_local_operator():
    from qa_mcp.web.auth import AuthenticationMiddleware
    from qa_mcp.core.security.actor import LOCAL_OPERATOR

    settings = {
        "mode": "development",
        "development_subject": "local-operator",
    }

    middleware = object.__new__(AuthenticationMiddleware)
    middleware.settings = settings

    request = Request({"type": "http", "method": "GET", "path": "/"})
    actor = middleware._session_actor(request)

    assert actor is not None
    assert actor is LOCAL_OPERATOR
    assert actor.local_operator is True
