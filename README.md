# ContextBridge MCP Server (Enterprise Modular)

FastAPI-based MCP server refactored for enterprise-oriented architecture:

- Modular codebase by domain (`core`, `services`, `api/routes`)
- Pluggable auth backend (`AUTH_BACKEND=demo` or `AUTH_BACKEND=oidc`)
- Scope-based authorization at MCP method/tool level
- Client allowlist for demo token endpoint
- Request correlation IDs via middleware
- Unique feature: policy simulation endpoint (`/auth/policy/preview`)
- Practical tool: live URL health check (`url_health_check`)

## Folder Structure

```text
FastMCP/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── mcp.py
│   │       └── public.py
│   ├── core/
│   │   ├── config.py
│   │   ├── request_context.py
│   │   └── security.py
│   ├── services/
│   │   ├── mcp_service.py
│   │   └── tools.py
│   ├── dependencies.py
│   └── main.py
├── main.py
├── .env.example
├── requirements.txt
└── README.md
```

## Enterprise Auth Model

1. `MCP_AUTH_MODE` controls accepted credential types at `/mcp`.
2. `AUTH_BACKEND` controls bearer token validation strategy.
3. Scope enforcement is centralized for `initialize`, `tools/list`, and `tools/call`.

Modes:

- `MCP_AUTH_MODE=oauth2`: Bearer only (recommended for production)
- `MCP_AUTH_MODE=api_key`: API key only
- `MCP_AUTH_MODE=both`: either API key or Bearer

Backends:

- `AUTH_BACKEND=oidc`: validate external JWT using issuer/audience/JWKS
- `AUTH_BACKEND=demo`: issue and validate opaque in-memory demo tokens

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy values from `.env.example`.

3. Start server:

```bash
python main.py
```

4. Validate health:

```http
GET /healthz
```

## Postman Validation (Demo Backend)

Use this when `AUTH_BACKEND=demo`.

1. Token request (`POST /oauth2/token`, `x-www-form-urlencoded`):

- `grant_type=client_credentials`
- `client_id=person1`
- `client_secret=person1-secret`
- `scope=mcp:initialize mcp:tools:list`

2. MCP initialize (`POST /mcp`, raw JSON):

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
```

Headers:

```http
Content-Type: application/json
Authorization: Bearer <access_token>
```

3. Access check:

- `tools/list` should pass with `mcp:tools:list`
- `tools/call` should fail unless `mcp:tools:call` or `mcp:tools:call:<tool_name>` is present

4. Real utility tool example (`url_health_check`):

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "url_health_check",
    "arguments": {
      "url": "https://www.github.com",
      "timeout_seconds": 5
    }
  }
}
```

Scope needed:

- `mcp:tools:call:url_health_check` or broader `mcp:tools:call`

## Unique Feature: Policy Preview

`POST /auth/policy/preview` lets security teams test policy outcomes before calling MCP.

Body:

```json
{
  "method": "tools/call",
  "tool_name": "greet_user"
}
```

Response includes:

- principal
- auth type
- required scope
- granted scopes
- allow/deny decision
- request ID

## Production Guidance

For enterprise deployment:

1. Set `AUTH_BACKEND=oidc`
2. Set `MCP_AUTH_MODE=oauth2`
3. Configure `OIDC_ISSUER_URL` and `OIDC_AUDIENCE`
4. Disable demo token endpoint usage
5. Keep API key mode off in production

