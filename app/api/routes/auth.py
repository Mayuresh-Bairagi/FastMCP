from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.dependencies import mcp_service, security_service, settings


router = APIRouter(tags=["auth"])


@router.post("/oauth2/token", summary="Issue token in demo backend")
async def oauth2_token(request: Request):
    cfg = settings()
    security = security_service()

    if cfg.auth_backend != "demo":
        return JSONResponse(
            {
                "error": "unsupported_in_environment",
                "error_description": "Token issuance is disabled when AUTH_BACKEND=oidc. Obtain token from your identity provider.",
            },
            status_code=400,
        )

    content_type = request.headers.get("content-type", "").lower()
    if not content_type.startswith("application/x-www-form-urlencoded"):
        return JSONResponse(
            {
                "error": "invalid_request",
                "error_description": "Content-Type must be application/x-www-form-urlencoded.",
            },
            status_code=400,
        )

    form_data = parse_qs((await request.body()).decode("utf-8"), keep_blank_values=True)
    grant_type = form_data.get("grant_type", [""])[0].strip().lower()
    client_id = form_data.get("client_id", [""])[0].strip()
    client_secret = form_data.get("client_secret", [""])[0].strip()
    scope = form_data.get("scope", [""])[0].strip()

    if grant_type not in {"client_credentials", "client-credentials"}:
        return JSONResponse(
            {
                "error": "unsupported_grant_type",
                "error_description": "Only client_credentials is supported.",
            },
            status_code=400,
        )

    response = security.issue_demo_token(client_id, client_secret, scope)
    if not response:
        return JSONResponse({"error": "server_error", "error_description": "Token service unavailable."}, status_code=500)

    status = int(response.pop("status", 200))
    return JSONResponse(response, status_code=status)


@router.post("/auth/policy/preview", summary="Preview authorization decision")
async def policy_preview(request: Request):
    body = await request.json()
    method = body.get("method", "")
    tool_name = body.get("tool_name", "")

    security = security_service()
    auth_ctx = security.authenticate(request)
    if not auth_ctx.authenticated:
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    decision = mcp_service().policy_decision(auth_ctx, method=method, tool_name=tool_name)
    decision["requestId"] = getattr(request.state, "request_id", "")
    return decision
