from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import time


def list_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "greet_user",
            "description": "Returns a greeting message for a provided name.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name to greet", "default": "World"}
                },
            },
        },
        {
            "name": "calculate",
            "description": "Performs add, subtract, multiply, or divide on two numbers.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                    "operation": {
                        "type": "string",
                        "description": "add | subtract | multiply | divide",
                        "default": "add",
                    },
                },
                "required": ["a", "b"],
            },
        },
        {
            "name": "get_weather",
            "description": "Returns mock weather data for a city.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"],
            },
        },
        {
            "name": "reverse_string",
            "description": "Returns the reverse of the provided text.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to reverse"}
                },
                "required": ["text"],
            },
        },
        {
            "name": "url_health_check",
            "description": "Checks whether a real HTTP/HTTPS endpoint is reachable and reports status and latency.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Absolute http/https URL to check"},
                    "timeout_seconds": {
                        "type": "number",
                        "description": "Request timeout in seconds",
                        "default": 5,
                    },
                },
                "required": ["url"],
            },
        },
    ]


def call_tool(tool_name: str, args: dict[str, Any], server_name: str) -> dict[str, Any]:
    if tool_name == "greet_user":
        name = args.get("name", "World")
        return {"message": f"Hello, {name}! Welcome to the {server_name}."}

    if tool_name == "calculate":
        a = float(args.get("a", 0))
        b = float(args.get("b", 0))
        operation = args.get("operation", "add")
        ops = {
            "add": a + b,
            "subtract": a - b,
            "multiply": a * b,
            "divide": a / b if b != 0 else None,
        }
        if operation not in ops:
            return {"error": f"Unknown operation '{operation}'."}
        if ops[operation] is None:
            return {"error": "Division by zero is not allowed."}
        return {"a": a, "b": b, "operation": operation, "result": ops[operation]}

    if tool_name == "get_weather":
        city = args.get("city", "")
        mock_data = {
            "new york": {"temp_c": 15, "condition": "Partly Cloudy", "humidity": 60},
            "london": {"temp_c": 10, "condition": "Rainy", "humidity": 80},
            "tokyo": {"temp_c": 22, "condition": "Sunny", "humidity": 55},
            "paris": {"temp_c": 13, "condition": "Overcast", "humidity": 70},
            "sydney": {"temp_c": 28, "condition": "Clear", "humidity": 45},
        }
        return {"city": city, **mock_data.get(city.lower(), {"temp_c": 20, "condition": "Unknown", "humidity": 50})}

    if tool_name == "reverse_string":
        text = args.get("text", "")
        return {"original": text, "reversed": text[::-1]}

    if tool_name == "url_health_check":
        raw_url = str(args.get("url", "")).strip()
        timeout_seconds = float(args.get("timeout_seconds", 5))

        parsed = urlparse(raw_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return {
                "reachable": False,
                "error": "Invalid URL. Provide an absolute http/https URL.",
            }

        start = time.perf_counter()
        try:
            request = Request(raw_url, method="GET", headers={"User-Agent": f"{server_name}/health-check"})
            with urlopen(request, timeout=timeout_seconds) as response:
                latency_ms = round((time.perf_counter() - start) * 1000, 2)
                status_code = int(getattr(response, "status", 0) or 0)
                return {
                    "reachable": 200 <= status_code < 400,
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                    "checked_url": raw_url,
                }
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "reachable": False,
                "error": str(exc),
                "latency_ms": latency_ms,
                "checked_url": raw_url,
            }

    raise KeyError(tool_name)
