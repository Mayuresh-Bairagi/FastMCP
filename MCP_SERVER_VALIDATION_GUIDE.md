# MCP Server Validation Guide (Platform Independent)

This guide explains how an MCP server should behave regardless of technology stack (Python, Node.js, Java, .NET, Go, etc.).

Use this before connecting your server to clients like Copilot Studio, custom agents, or desktop tools.

## 1. What an MCP server should expose

At minimum, your server should support JSON-RPC 2.0 MCP methods over an agreed transport.

Common transport styles:
- Streamable HTTP: single HTTP endpoint, typically `POST /mcp`
- SSE-based MCP: usually split endpoints such as stream endpoint and message endpoint

Important:
- A browser sends `GET` by default.
- If your MCP endpoint supports only `POST`, opening it in a browser can show `405 Method Not Allowed`. This is normal.

## 2. Protocol-level expectations

MCP clients typically call methods in this order:
1. `initialize`
2. `tools/list`
3. `tools/call` (one or more times)

### 2.1 `initialize`
Purpose:
- Handshake with protocol version
- Capability negotiation

Typical request:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "postman",
      "version": "1.0"
    }
  }
}
```

Typical response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "Your MCP Server",
      "version": "1.0.0"
    }
  }
}
```

Note:
- `capabilities.tools` being `{}` is valid. It indicates support, not the tool list.

### 2.2 `tools/list`
Purpose:
- Return all callable tools and their input schemas.

Typical request:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

Typical response shape:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "tool_name",
        "description": "What this tool does",
        "inputSchema": {
          "type": "object",
          "properties": {
            "param1": { "type": "string" }
          },
          "required": ["param1"]
        }
      }
    ]
  }
}
```

### 2.3 `tools/call`
Purpose:
- Execute a specific tool with arguments.

Typical request:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value"
    }
  }
}
```

Typical response shape:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Tool output"
      }
    ]
  }
}
```

## 3. Postman validation checklist

Use this exact checklist before client integration.

### Request setup (for each call)
- Method: `POST`
- URL: `https://your-domain.com/mcp`
- Header: `Content-Type: application/json`
- Header: `x-api-key: <your-api-key>` if the server uses API key authentication
- Body type: raw JSON

### Run sequence
1. Send `initialize`
- Expect HTTP 200
- Expect `result.serverInfo`
- Expect `result.protocolVersion`

2. Send `tools/list`
- Expect HTTP 200
- Expect non-empty `result.tools`
- Validate tool names and schemas

3. Send `tools/call`
- Expect HTTP 200
- Expect `result.content` with useful output

### Pass criteria
- All three methods return JSON-RPC responses
- IDs in response match request IDs
- No HTML error page returned
- No transport mismatch errors

## 4. Common failures and fixes

### Error: `405 Method Not Allowed` on `/mcp`
Cause:
- Sending `GET` to a `POST` endpoint
- Or transport mismatch (SSE endpoint used as Streamable HTTP)

Fix:
- Use `POST` in Postman
- Verify your server supports the transport required by your client

### Error: `500 Internal Server Error`
Cause:
- Server-side exception while parsing request or processing method

Fix:
- Check server logs
- Confirm body is valid JSON
- Confirm required fields exist: `jsonrpc`, `id`, `method`

### Error: `401 Unauthorized`
Cause:
- Missing API key
- Invalid API key

Fix:
- Send the expected auth header such as `x-api-key`
- Confirm the client and server are using the same key value

### Error: tools missing after initialize
Cause:
- Misunderstanding protocol

Fix:
- Call `tools/list` to retrieve tool definitions

### Error: client connect fails but Postman works
Cause:
- Client expects specific transport/version/security behavior

Fix:
- Verify protocol version compatibility
- Verify required OpenAPI metadata if client imports via connector
- Verify authentication settings (if enabled)

## 5. Transport compatibility notes

Before integration, confirm what your target client expects:
- Streamable HTTP only
- SSE MCP only
- Both

If your server framework defaults to one transport, do not assume it supports the other automatically.

## 6. Optional OpenAPI (for connector-based clients)

Some platforms import MCP servers via OpenAPI/Swagger metadata. For those:
- Ensure endpoint path is correct (example: `/mcp`)
- Ensure HTTP method is correct (`POST`)
- Include required vendor extension keys if platform requires them

Example (Swagger 2.0 field often required by Copilot Studio):
- `x-ms-agentic-protocol: mcp-streamable-1.0`

## 7. Production readiness checks (tech agnostic)

Before production use:
- Add request logging with correlation IDs
- Add input validation and clear JSON-RPC error responses
- Add authentication/authorization if needed
- Add timeout and retry strategy
- Add health endpoint (for uptime checks)
- Add monitoring and alerting

## 8. Quick go/no-go checklist

Mark each item before connecting any client:
- `[ ]` `POST /mcp` reachable over HTTPS
- `[ ]` `initialize` succeeds
- `[ ]` `tools/list` returns expected tool schemas
- `[ ]` `tools/call` returns expected result format
- `[ ]` Transport type matches client requirement
- `[ ]` No 4xx/5xx errors in logs during test flow

If all are checked, your MCP server is integration-ready.
