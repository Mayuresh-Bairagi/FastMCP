import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    server_name: str = os.getenv("SERVER_NAME", "ContextBridge MCP Server")
    server_version: str = os.getenv("SERVER_VERSION", "2.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Auth mode for MCP endpoint: api_key | oauth2 | both
    mcp_auth_mode: str = os.getenv("MCP_AUTH_MODE", "oauth2").strip().lower()

    # Auth backend for bearer tokens: demo | oidc
    auth_backend: str = os.getenv("AUTH_BACKEND", "demo").strip().lower()

    # API key support (normally disabled in enterprise prod)
    mcp_api_key: str = os.getenv("MCP_API_KEY", "change-me-demo-key")

    # OIDC/JWT settings (enterprise)
    oidc_issuer_url: str = os.getenv("OIDC_ISSUER_URL", "").strip()
    oidc_audience: str = os.getenv("OIDC_AUDIENCE", "").strip()
    oidc_jwks_url: str = os.getenv("OIDC_JWKS_URL", "").strip()

    # Demo OAuth token endpoint settings (dev fallback)
    mcp_oauth_client_id: str = os.getenv("MCP_OAUTH_CLIENT_ID", "demo-client")
    mcp_oauth_client_secret: str = os.getenv("MCP_OAUTH_CLIENT_SECRET", "change-me-demo-secret")
    mcp_oauth_clients: str = os.getenv("MCP_OAUTH_CLIENTS", "").strip()
    mcp_oauth_token_ttl_seconds: int = int(os.getenv("MCP_OAUTH_TOKEN_TTL_SECONDS", "3600"))

    mcp_oauth_allowed_scopes_raw: str = os.getenv(
        "MCP_OAUTH_ALLOWED_SCOPES",
        "mcp:initialize mcp:tools:list mcp:tools:call mcp:tools:call:greet_user mcp:tools:call:calculate mcp:tools:call:get_weather mcp:tools:call:reverse_string mcp:tools:call:url_health_check",
    )
    mcp_oauth_default_scopes_raw: str = os.getenv(
        "MCP_OAUTH_DEFAULT_SCOPES",
        "mcp:initialize mcp:tools:list",
    )

    @property
    def oidc_jwks_effective_url(self) -> str:
        if self.oidc_jwks_url:
            return self.oidc_jwks_url
        if not self.oidc_issuer_url:
            return ""
        return f"{self.oidc_issuer_url.rstrip('/')}/discovery/v2.0/keys"

    @property
    def mcp_oauth_allowed_scopes(self) -> set[str]:
        return {value.strip() for value in self.mcp_oauth_allowed_scopes_raw.split() if value.strip()}

    @property
    def mcp_oauth_default_scopes(self) -> set[str]:
        return {value.strip() for value in self.mcp_oauth_default_scopes_raw.split() if value.strip()}


def get_settings() -> Settings:
    return Settings()
