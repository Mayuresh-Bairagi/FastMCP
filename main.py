from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

description = """
## Demo MCP Server

This is a **demo MCP (Model Context Protocol) server** built with [FastAPI](https://fastapi.tiangolo.com/)
and [fastapi-mcp](https://github.com/tadata-org/fastapi_mcp). It is intended for learning and demonstration purposes only.

### What is MCP?
The **Model Context Protocol (MCP)** is an open standard that allows AI models (like Claude, GitHub Copilot, etc.)
to connect to external tools and data sources through a unified interface.

### Available Tools

| Tool | Description |
|---|---|
| 🙋 **Greet User** | Returns a personalized greeting |
| 🧮 **Calculator** | Performs basic arithmetic (add, subtract, multiply, divide) |
| 🌤️ **Mock Weather** | Returns simulated weather data for a city |
| 🔄 **Reverse String** | Reverses the characters in any string |

### MCP Endpoint
Connect any MCP-compatible client to: **`/mcp`**
"""

app = FastAPI(
    title="Demo MCP Server",
    description=description,
    version="1.0.0",
    contact={
        "name": "Demo Project",
    },
    license_info={
        "name": "MIT",
    },
)


@app.get("/", operation_id="landing_page", summary="Show route guide")
def landing_page() -> dict:
    """Return a route catalog with inputs, outputs, and usage examples."""
    return {
        "service": "Demo MCP Server",
        "version": "1.0.0",
        "description": "Landing route with documentation for all available routes.",
        "routes": [
            {
                "name": "Landing Page",
                "method": "GET",
                "path": "/",
                "description": "Shows all routes with input/output expectations.",
                "how_to_access": "GET /",
                "input": "No query parameters required.",
                "expected_output": {
                    "service": "Demo MCP Server",
                    "routes": "List of route documentation objects",
                },
            },
            {
                "name": "Greet User",
                "method": "GET",
                "path": "/greet",
                "description": "Returns a greeting message for a provided name.",
                "how_to_access": "GET /greet?name=Alice",
                "input": {
                    "name": {
                        "type": "string",
                        "required": False,
                        "default": "World",
                    }
                },
                "expected_output": {
                    "message": "Hello, Alice! Welcome to the Demo MCP Server.",
                },
            },
            {
                "name": "Calculator",
                "method": "GET",
                "path": "/calculate",
                "description": "Performs add, subtract, multiply, or divide on two numbers.",
                "how_to_access": "GET /calculate?a=10&b=3&operation=multiply",
                "input": {
                    "a": {"type": "number", "required": True},
                    "b": {"type": "number", "required": True},
                    "operation": {
                        "type": "string",
                        "required": False,
                        "default": "add",
                        "allowed": ["add", "subtract", "multiply", "divide"],
                    },
                },
                "expected_output": {
                    "a": 10,
                    "b": 3,
                    "operation": "multiply",
                    "result": 30,
                },
            },
            {
                "name": "Mock Weather",
                "method": "GET",
                "path": "/weather",
                "description": "Returns demo weather details for a city.",
                "how_to_access": "GET /weather?city=Tokyo",
                "input": {
                    "city": {"type": "string", "required": True},
                },
                "expected_output": {
                    "city": "Tokyo",
                    "temp_c": 22,
                    "condition": "Sunny",
                    "humidity": 55,
                },
            },
            {
                "name": "Reverse String",
                "method": "GET",
                "path": "/reverse",
                "description": "Returns the reverse of the provided text.",
                "how_to_access": "GET /reverse?text=hello",
                "input": {
                    "text": {"type": "string", "required": True},
                },
                "expected_output": {
                    "original": "hello",
                    "reversed": "olleh",
                },
            },
            {
                "name": "MCP Endpoint",
                "method": "GET/POST (managed by MCP client)",
                "path": "/mcp",
                "description": "MCP transport endpoint used by MCP-compatible clients.",
                "how_to_access": "Configure MCP client with URL: /mcp (or https://your-domain.com/mcp)",
                "input": "MCP protocol messages from client.",
                "expected_output": "MCP protocol responses.",
            },
        ],
    }


# ── Tool 1: Greet a user ──────────────────────────────────────────────────────
@app.get("/greet", operation_id="greet_user", summary="Greet a user by name")
def greet_user(name: str = "World") -> dict:
    """Return a friendly greeting for the given name."""
    return {"message": f"Hello, {name}! Welcome to the Demo MCP Server."}


# ── Tool 2: Basic calculator ──────────────────────────────────────────────────
@app.get(
    "/calculate",
    operation_id="calculate",
    summary="Perform a basic arithmetic operation",
)
def calculate(a: float, b: float, operation: str = "add") -> dict:
    """
    Perform one of four arithmetic operations on two numbers.

    - operation: add | subtract | multiply | divide
    """
    ops = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else None,
    }
    if operation not in ops:
        return {"error": f"Unknown operation '{operation}'. Use: add, subtract, multiply, divide"}
    result = ops[operation]
    if result is None:
        return {"error": "Division by zero is not allowed"}
    return {"a": a, "b": b, "operation": operation, "result": result}


# ── Tool 3: Mock weather info ─────────────────────────────────────────────────
@app.get(
    "/weather",
    operation_id="get_weather",
    summary="Get mock weather for a city",
)
def get_weather(city: str) -> dict:
    """Return mock weather data for demonstration purposes."""
    mock_data = {
        "new york": {"temp_c": 15, "condition": "Partly Cloudy", "humidity": 60},
        "london": {"temp_c": 10, "condition": "Rainy", "humidity": 80},
        "tokyo": {"temp_c": 22, "condition": "Sunny", "humidity": 55},
        "paris": {"temp_c": 13, "condition": "Overcast", "humidity": 70},
        "sydney": {"temp_c": 28, "condition": "Clear", "humidity": 45},
    }
    key = city.lower()
    if key in mock_data:
        return {"city": city, **mock_data[key]}
    return {"city": city, "temp_c": 20, "condition": "Unknown", "humidity": 50}


# ── Tool 4: Reverse a string ──────────────────────────────────────────────────
@app.get(
    "/reverse",
    operation_id="reverse_string",
    summary="Reverse a given string",
)
def reverse_string(text: str) -> dict:
    """Reverse the characters in the provided text."""
    return {"original": text, "reversed": text[::-1]}


# ── MCP Streamable HTTP endpoint (POST /mcp) ────────────────────────────────
# Implements MCP Streamable HTTP transport (mcp-streamable-1.0) for
# Microsoft Copilot Studio and other MCP-compatible clients.

@app.post("/mcp", operation_id="InvokeMCP", summary="MCP Streamable HTTP endpoint")
async def mcp_streamable_http(request: Request):
    """
    Streamable HTTP transport handler for MCP-compatible clients (e.g. Microsoft Copilot Studio).
    Accepts JSON-RPC 2.0 messages and returns MCP responses.
    """
    body = await request.json()
    method = body.get("method", "")
    req_id = body.get("id", 1)

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "Demo MCP Server",
                    "version": "1.0.0"
                }
            }
        })

    if method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "greet_user",
                        "description": "Returns a greeting message for a provided name.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Name to greet", "default": "World"}
                            }
                        }
                    },
                    {
                        "name": "calculate",
                        "description": "Performs add, subtract, multiply, or divide on two numbers.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "a": {"type": "number", "description": "First number"},
                                "b": {"type": "number", "description": "Second number"},
                                "operation": {"type": "string", "description": "add | subtract | multiply | divide", "default": "add"}
                            },
                            "required": ["a", "b"]
                        }
                    },
                    {
                        "name": "get_weather",
                        "description": "Returns mock weather data for a city.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City name"}
                            },
                            "required": ["city"]
                        }
                    },
                    {
                        "name": "reverse_string",
                        "description": "Returns the reverse of the provided text.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Text to reverse"}
                            },
                            "required": ["text"]
                        }
                    }
                ]
            }
        })

    if method == "tools/call":
        tool_name = body.get("params", {}).get("name", "")
        args = body.get("params", {}).get("arguments", {})

        if tool_name == "greet_user":
            name = args.get("name", "World")
            result = {"message": f"Hello, {name}! Welcome to the Demo MCP Server."}

        elif tool_name == "calculate":
            a = float(args.get("a", 0))
            b = float(args.get("b", 0))
            operation = args.get("operation", "add")
            ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b if b != 0 else None}
            if operation not in ops:
                result = {"error": f"Unknown operation '{operation}'."}
            elif ops[operation] is None:
                result = {"error": "Division by zero is not allowed."}
            else:
                result = {"a": a, "b": b, "operation": operation, "result": ops[operation]}

        elif tool_name == "get_weather":
            city = args.get("city", "")
            mock_data = {
                "new york": {"temp_c": 15, "condition": "Partly Cloudy", "humidity": 60},
                "london": {"temp_c": 10, "condition": "Rainy", "humidity": 80},
                "tokyo": {"temp_c": 22, "condition": "Sunny", "humidity": 55},
                "paris": {"temp_c": 13, "condition": "Overcast", "humidity": 70},
                "sydney": {"temp_c": 28, "condition": "Clear", "humidity": 45},
            }
            result = {"city": city, **mock_data.get(city.lower(), {"temp_c": 20, "condition": "Unknown", "humidity": 50})}

        elif tool_name == "reverse_string":
            text = args.get("text", "")
            result = {"original": text, "reversed": text[::-1]}

        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found."}
            })

        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": str(result)}]
            }
        })

    # Unknown method
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not supported."}
    }, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
