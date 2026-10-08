from __future__ import annotations

import re
import secrets
import time
import uuid
from contextvars import Token

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from qa_mcp.core.security.actor import Actor, reset_current_actor, set_current_actor
from qa_mcp.core.security.authorization import AuthorizationError, ProjectAuthorization


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: dict, authorization: ProjectAuthorization, audit_repository):
        super().__init__(app)
        self.settings = settings
        self.authorization = authorization
        self.audit_repository = audit_repository

    @staticmethod
    def _public_path(path: str) -> bool:
        return (
            path.startswith("/static/")
            or path in {"/auth/login", "/auth/callback", "/auth/logout", "/health/live", "/api/health", "/api/ready"}
        )

    def _session_actor(self, request: Request) -> Actor | None:
        if self.settings["mode"] == "development":
            return Actor(
                subject=self.settings.get("development_subject", "local-development"),
                email=self.settings.get("development_email", "local-development@localhost"),
            )
        session = request.session
        subject = session.get("actor_sub")
        email = session.get("actor_email")
        expires_at = session.get("expires_at", 0)
        if (
            not isinstance(subject, str)
            or not subject
            or not isinstance(email, str)
            or not email
            or not isinstance(expires_at, (int, float))
            or expires_at <= time.time()
        ):
            return None
        return Actor(subject=subject, email=email)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        raw_request_id = request.headers.get("x-request-id", "")
        request_id = (
            raw_request_id
            if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", raw_request_id)
            else uuid.uuid4().hex
        )
        request.state.request_id = request_id
        actor = self._session_actor(request)
        if not self._public_path(path) and actor is None:
            if not path.startswith("/api/"):
                response = HTMLResponse(
                    '<main><h1>Sign in required</h1>'
                    '<p>Your QA-MCP session is missing or expired.</p>'
                    '<a href="/auth/login">Sign in with Google</a></main>',
                    status_code=401,
                )
            else:
                response = JSONResponse(
                    {"detail": "Authentication required"}, status_code=401
                )
            response.headers["X-Request-ID"] = request_id
            return response

        if (
            actor is not None
            and self.settings["mode"] == "google"
            and request.method in {"POST", "PUT", "PATCH", "DELETE"}
            and path != "/auth/callback"
        ):
            expected = request.session.get("csrf_token", "")
            cookie = request.cookies.get("qa_csrf", "")
            supplied = request.headers.get("x-csrf-token", "")
            if (
                not expected
                or not cookie
                or not supplied
                or not secrets.compare_digest(expected, cookie)
                or not secrets.compare_digest(expected, supplied)
            ):
                response = JSONResponse(
                    {"detail": "CSRF validation failed"}, status_code=403
                )
                response.headers["X-Request-ID"] = request_id
                return response
        token: Token = set_current_actor(actor) if actor is not None else None
        try:
            response = await call_next(request)
        finally:
            if token is not None:
                reset_current_actor(token)

        response.headers["X-Request-ID"] = request_id
        if actor is not None and self.settings["mode"] == "google":
            csrf = request.session.get("csrf_token")
            if not csrf:
                csrf = secrets.token_urlsafe(32)
                request.session["csrf_token"] = csrf
            response.set_cookie(
                "qa_csrf",
                csrf,
                max_age=self.settings["session_max_age_seconds"],
                secure=self.settings["cookie_secure"],
                httponly=False,
                samesite="lax",
                path="/",
            )

        if actor is not None and self._is_audited(request):
            project_id = self._project_id(path)
            try:
                self.audit_repository.record_audit(
                    actor.subject,
                    project_id,
                    f"{request.method}:{path}",
                    "success" if response.status_code < 400 else f"http_{response.status_code}",
                    request_id,
                )
            except Exception:
                # Audit storage failure is observable in server logs, without
                # request bodies, credentials, or execution output.
                import logging

                logging.getLogger(__name__).exception("Security audit write failed")
        return response

    @staticmethod
    def _is_audited(request: Request) -> bool:
        path = request.url.path
        return (
            request.method in {"POST", "PUT", "PATCH", "DELETE"}
            or path.startswith("/api/projects/")
            or path.startswith("/api/executions")
        )

    @staticmethod
    def _project_id(path: str) -> str | None:
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[:2] == ["api", "projects"]:
            return parts[2][:200]
        return None


def install_authentication_middleware(app, settings, authorization, audit_repository):
    if settings["mode"] not in {"google", "development"}:
        raise RuntimeError("QA_AUTH_MODE must be google or development")
    environment = settings.get("environment", "local").lower()
    if environment in {"prod", "production"} and settings["mode"] != "google":
        raise RuntimeError("Production requires Google OIDC authentication")
    if settings["mode"] == "google":
        required = (
            "google_client_id",
            "google_client_secret",
            "redirect_uri",
            "workspace_domain",
            "session_secret",
        )
        missing = [name for name in required if not settings.get(name)]
        if missing:
            raise RuntimeError(
                "Google OIDC configuration is incomplete: " + ", ".join(missing)
            )
        if len(settings["session_secret"]) < 32:
            raise RuntimeError("QA_SESSION_SECRET must contain at least 32 characters")
        if environment in {"prod", "production"} and not settings["cookie_secure"]:
            raise RuntimeError("Production Google OIDC sessions require Secure cookies")
        if environment in {"prod", "production"} and not settings["redirect_uri"].startswith("https://"):
            raise RuntimeError("Production Google OIDC redirect URI must use HTTPS")
        if settings["session_max_age_seconds"] < 300:
            raise RuntimeError("QA_SESSION_MAX_AGE_SECONDS must be at least 300")
        if environment in {"prod", "production"} and not settings.get(
            "global_admin_subjects"
        ):
            raise RuntimeError(
                "Production requires at least one configured global administrator subject"
            )

    from starlette.middleware.sessions import SessionMiddleware

    secret = settings.get("session_secret") or "development-only-session-secret-change-me"
    # AuthenticationMiddleware must be inside SessionMiddleware so request.session
    # is available. Starlette inserts middleware at the front of its stack.
    app.add_middleware(
        AuthenticationMiddleware,
        settings=settings,
        authorization=authorization,
        audit_repository=audit_repository,
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=secret,
        session_cookie="qa_session",
        max_age=settings["session_max_age_seconds"],
        same_site="lax",
        https_only=settings["cookie_secure"],
    )


def install_auth_exception_handler(app):
    @app.exception_handler(AuthorizationError)
    async def authorization_error_handler(request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=403)
