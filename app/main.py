from fastapi import FastAPI

from app.api.routes import auth, mcp, public
from app.core.request_context import RequestContextMiddleware
from app.dependencies import settings


def create_app() -> FastAPI:
    cfg = settings()

    app = FastAPI(
        title=cfg.server_name,
        description="Enterprise-ready modular MCP server with pluggable auth backends.",
        version=cfg.server_version,
        contact={"name": "Platform Team"},
        license_info={"name": "MIT"},
    )

    app.add_middleware(RequestContextMiddleware)

    app.include_router(public.router)
    app.include_router(auth.router)
    app.include_router(mcp.router)

    return app


app = create_app()
