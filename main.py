from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

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


# ── Mount MCP on /mcp ─────────────────────────────────────────────────────────
mcp = FastApiMCP(app)
mcp.mount()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
