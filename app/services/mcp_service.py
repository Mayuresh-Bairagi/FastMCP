from typing import Any

from app.core.config import Settings
from app.core.security import AuthContext, SecurityService
from app.services.tools import call_tool, list_tools


class MCPService:
    def __init__(self, settings: Settings, security: SecurityService):
        self.settings = settings
        self.security = security

    @staticmethod
    def _jsonrpc_error(req_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}

    @staticmethod
    def _required_scope_for_method(method: str, body: dict[str, Any]) -> str | None:
        if method == "initialize":
            return "mcp:initialize"
        if method == "tools/list":
            return "mcp:tools:list"
        if method == "tools/call":
            tool_name = body.get("params", {}).get("name", "")
            return f"mcp:tools:call:{tool_name}" if tool_name else "mcp:tools:call"
        return None

    def policy_decision(self, auth_context: AuthContext, method: str, tool_name: str = "") -> dict[str, Any]:
        if method == "tools/call":
            required_scope = f"mcp:tools:call:{tool_name}" if tool_name else "mcp:tools:call"
        elif method == "initialize":
            required_scope = "mcp:initialize"
        elif method == "tools/list":
            required_scope = "mcp:tools:list"
        else:
            required_scope = "unknown"

        allowed = self.security.has_scope(auth_context.scopes, required_scope)
        return {
            "principal": auth_context.principal,
            "authType": auth_context.auth_type,
            "requiredScope": required_scope,
            "grantedScopes": sorted(auth_context.scopes),
            "allowed": allowed,
        }

    def handle_request(self, body: dict[str, Any], auth_context: AuthContext) -> tuple[int, dict[str, Any]]:
        method = body.get("method", "")
        req_id = body.get("id", 1)

        required_scope = self._required_scope_for_method(method, body)
        if required_scope and not self.security.has_scope(auth_context.scopes, required_scope):
            return 403, self._jsonrpc_error(req_id, -32003, f"Insufficient scope. Required: {required_scope}")

        if method == "initialize":
            return 200, {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": self.settings.server_name,
                        "version": self.settings.server_version,
                    },
                },
            }

        if method == "tools/list":
            return 200, {"jsonrpc": "2.0", "id": req_id, "result": {"tools": list_tools()}}

        if method == "tools/call":
            tool_name = body.get("params", {}).get("name", "")
            args = body.get("params", {}).get("arguments", {})
            try:
                result = call_tool(tool_name, args, self.settings.server_name)
            except KeyError:
                return 200, self._jsonrpc_error(req_id, -32601, f"Tool '{tool_name}' not found.")

            return 200, {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": str(result)}]},
            }

        return 200, self._jsonrpc_error(req_id, -32601, f"Method '{method}' not supported.")
