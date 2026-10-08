from __future__ import annotations

from authlib.integrations.starlette_client import OAuth

from qa_mcp.core.security.actor import Actor


class GoogleOIDCProvider:
    """Google OIDC Authorization Code flow with Authlib claim validation."""

    def __init__(self, settings: dict):
        self.settings = settings
        self.oauth = OAuth()
        self.oauth.register(
            name="google",
            client_id=settings["google_client_id"],
            client_secret=settings["google_client_secret"],
            server_metadata_url=(
                "https://accounts.google.com/.well-known/openid-configuration"
            ),
            client_kwargs={"scope": "openid email profile"},
        )

    async def begin(self, request):
        return await self.oauth.google.authorize_redirect(
            request,
            redirect_uri=self.settings["redirect_uri"],
        )

    async def complete(self, request) -> Actor:
        # Authlib validates the discovery issuer, signature against Google's
        # JWKS, audience/client ID, expiry, and the nonce saved in the session.
        token = await self.oauth.google.authorize_access_token(request)
        claims = token.get("userinfo")
        if not claims:
            raise ValueError("Google OIDC identity claims are missing")

        subject = claims.get("sub")
        email = claims.get("email")
        verified = claims.get("email_verified")
        hosted_domain = claims.get("hd")
        expected_domain = self.settings["workspace_domain"]

        if not isinstance(subject, str) or not subject:
            raise ValueError("Google OIDC subject is missing")
        if not isinstance(email, str) or not email or verified is not True:
            raise ValueError("Google account email is not verified")
        if (
            not expected_domain
            or not isinstance(hosted_domain, str)
            or hosted_domain.lower() != expected_domain
        ):
            raise ValueError("Google Workspace domain is not allowed")

        # Do not retain access/refresh/ID tokens in the application session.
        token.clear()
        return Actor(subject=subject, email=email, authenticated=True)
