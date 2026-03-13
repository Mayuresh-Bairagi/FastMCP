from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI(
    title="Demo MCP Server",
    description="A simple demo MCP server built with FastAPI and fastapi-mcp",
    version="1.0.0",
)


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
