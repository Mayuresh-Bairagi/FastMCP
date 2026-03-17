import hmac
import secrets
import time
from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import Request
from jwt import PyJWKClient
from jwt.types import Options

from app.core.config import Settings


@dataclass
class AuthContext:
    authenticated: bool
    principal: str
    auth_type: str
    scopes: set[str]
    claims: dict[str, Any]


class SecurityService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.issued_tokens: dict[str, dict[str, Any]] = {}
        self.allowed_clients = self._parse_oauth_clients(settings.mcp_oauth_clients)
        if not self.allowed_clients:
            self.allowed_clients = {settings.mcp_oauth_client_id: settings.mcp_oauth_client_secret}

        self.jwks_client = None
        if self.settings.auth_backend == "oidc" and self.settings.oidc_jwks_effective_url:
            self.jwks_client = PyJWKClient(self.settings.oidc_jwks_effective_url)

    @staticmethod
    def _parse_oauth_clients(raw_clients: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        if not raw_clients:
            return parsed

        for pair in raw_clients.split(","):
            if ":" not in pair:
                continue
            client_id, client_secret = pair.split(":", 1)
            client_id = client_id.strip()
            client_secret = client_secret.strip()
            if client_id and client_secret:
                parsed[client_id] = client_secret
        return parsed

    @staticmethod
    def _extract_bearer_token(request: Request) -> str:
        auth_header = request.headers.get("authorization", "")
        if not auth_header.lower().startswith("bearer "):
            return ""
        return auth_header.split(" ", 1)[1].strip()

    def _is_api_key_valid(self, request: Request) -> bool:
        provided_key = request.headers.get("x-api-key", "")
        return hmac.compare_digest(provided_key, self.settings.mcp_api_key)

    @staticmethod
    def _scope_set_from_claims(claims: dict[str, Any]) -> set[str]:
        scopes: set[str] = set()

        scope_value = claims.get("scope", "")
        if isinstance(scope_value, str):
            scopes.update(part for part in scope_value.split() if part)

        scp_value = claims.get("scp", "")
        if isinstance(scp_value, str):
            scopes.update(part for part in scp_value.split() if part)

        roles = claims.get("roles", [])
        if isinstance(roles, list):
            scopes.update(f"role:{role}" for role in roles if isinstance(role, str) and role)

        return scopes

    def _validate_demo_bearer(self, token: str) -> AuthContext:
        token_info = self.issued_tokens.get(token)
        if not token_info:
            return AuthContext(False, "anonymous", "bearer", set(), {})

        if int(time.time()) >= token_info["expires_at"]:
            self.issued_tokens.pop(token, None)
            return AuthContext(False, "anonymous", "bearer", set(), {})

        return AuthContext(
            authenticated=True,
            principal=token_info.get("client_id", "demo-client"),
            auth_type="bearer",
            scopes=set(token_info.get("scopes", set())),
            claims={"client_id": token_info.get("client_id", "demo-client")},
        )

    def _validate_oidc_bearer(self, token: str) -> AuthContext:
        if not self.jwks_client:
            return AuthContext(False, "anonymous", "bearer", set(), {})

        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            decode_options: Options = {"verify_aud": bool(self.settings.oidc_audience)}
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "RS384", "RS512", "ES256"],
                audience=self.settings.oidc_audience or None,
                issuer=self.settings.oidc_issuer_url or None,
                options=decode_options,
            )
        except Exception:
            return AuthContext(False, "anonymous", "bearer", set(), {})

        principal = str(
            claims.get("sub")
            or claims.get("azp")
            or claims.get("appid")
            or claims.get("client_id")
            or "oidc-principal"
        )
        scopes = self._scope_set_from_claims(claims)

        return AuthContext(True, principal, "bearer", scopes, claims)

    def authenticate(self, request: Request) -> AuthContext:
        mode = self.settings.mcp_auth_mode

        if mode in {"api_key", "both"} and self._is_api_key_valid(request):
            return AuthContext(True, "api-key-client", "api_key", {"*"}, {})

        if mode in {"oauth2", "both"}:
            token = self._extract_bearer_token(request)
            if token:
                if self.settings.auth_backend == "oidc":
                    return self._validate_oidc_bearer(token)
                return self._validate_demo_bearer(token)

        return AuthContext(False, "anonymous", "none", set(), {})

    @staticmethod
    def has_scope(granted_scopes: set[str], required_scope: str) -> bool:
        if "*" in granted_scopes or "mcp:*" in granted_scopes:
            return True
        if required_scope in granted_scopes:
            return True
        if required_scope.startswith("mcp:tools:call:") and "mcp:tools:call" in granted_scopes:
            return True
        return False

    def issue_demo_token(self, client_id: str, client_secret: str, requested_scope: str) -> dict[str, Any] | None:
        if self.settings.auth_backend != "demo":
            return None

        expected_secret = self.allowed_clients.get(client_id)
        if not expected_secret or not hmac.compare_digest(client_secret, expected_secret):
            return {"error": "invalid_client", "error_description": "Invalid client credentials.", "status": 401}

        requested_scopes = set(requested_scope.split()) if requested_scope else set(self.settings.mcp_oauth_default_scopes)
        if not requested_scopes:
            requested_scopes = set(self.settings.mcp_oauth_default_scopes)

        invalid_scopes = [scope for scope in requested_scopes if scope not in self.settings.mcp_oauth_allowed_scopes]
        if invalid_scopes:
            return {
                "error": "invalid_scope",
                "error_description": f"Unsupported scope(s): {', '.join(invalid_scopes)}",
                "status": 400,
            }

        token = secrets.token_urlsafe(32)
        expires_at = int(time.time()) + self.settings.mcp_oauth_token_ttl_seconds
        self.issued_tokens[token] = {
            "client_id": client_id,
            "scopes": set(requested_scopes),
            "expires_at": expires_at,
        }

        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": self.settings.mcp_oauth_token_ttl_seconds,
            "scope": " ".join(sorted(requested_scopes)),
            "status": 200,
        }
