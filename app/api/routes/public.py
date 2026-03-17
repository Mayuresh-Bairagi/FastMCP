from fastapi import APIRouter

from app.dependencies import settings


router = APIRouter()


@router.get("/healthz", tags=["system"], summary="Liveness probe")
def healthz() -> dict:
    cfg = settings()
    return {
        "status": "ok",
        "service": cfg.server_name,
        "version": cfg.server_version,
        "environment": cfg.environment,
        "authBackend": cfg.auth_backend,
    }


@router.get("/", tags=["system"], summary="Service overview")
def landing() -> dict:
    cfg = settings()
    return {
        "service": cfg.server_name,
        "version": cfg.server_version,
        "description": "Enterprise-style modular MCP server.",
        "routes": [
            {"method": "GET", "path": "/", "description": "Service overview"},
            {"method": "GET", "path": "/healthz", "description": "Health check"},
            {"method": "POST", "path": "/oauth2/token", "description": "Demo token endpoint (disabled in OIDC mode)"},
            {"method": "POST", "path": "/auth/policy/preview", "description": "Unique feature: scope policy decision preview"},
            {"method": "POST", "path": "/mcp", "description": "MCP Streamable HTTP endpoint"},
        ],
    }
