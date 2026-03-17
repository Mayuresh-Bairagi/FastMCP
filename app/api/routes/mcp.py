from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.dependencies import mcp_service, security_service, settings


router = APIRouter(tags=["mcp"])


def _auth_error_message() -> str:
    mode = settings().mcp_auth_mode
    if mode == "oauth2":
        return "Unauthorized. Provide a valid Authorization: Bearer <token> header."
    if mode == "both":
        return "Unauthorized. Provide a valid x-api-key or Authorization: Bearer <token> header."
    return "Unauthorized. Provide a valid x-api-key header."


@router.post("/mcp", operation_id="InvokeMCP", summary="MCP Streamable HTTP endpoint")
async def mcp_endpoint(request: Request):
    auth_ctx = security_service().authenticate(request)
    if not auth_ctx.authenticated:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32001, "message": _auth_error_message()},
            },
            status_code=401,
            headers={"WWW-Authenticate": 'Bearer realm="mcp"'},
        )

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Invalid or missing JSON body."},
            },
            status_code=400,
        )

    if not isinstance(body, dict):
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32600, "message": "Invalid Request. Expected a JSON object."},
            },
            status_code=400,
        )

    status_code, payload = mcp_service().handle_request(body, auth_ctx)
    return JSONResponse(payload, status_code=status_code)
