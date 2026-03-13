# Demo MCP Server with FastAPI

A simple demo **Model Context Protocol (MCP)** server built using [FastAPI](https://fastapi.tiangolo.com/) and [fastapi-mcp](https://github.com/tadata-org/fastapi_mcp). This project is for demonstration purposes only.

---

## Project Structure

```
FastMCP/
├── main.py           # FastAPI app with MCP tools
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## Tools Exposed

| Tool | Operation ID | Description |
|---|---|---|
| Greet User | `greet_user` | Returns a greeting for a given name |
| Calculator | `calculate` | Performs add / subtract / multiply / divide |
| Mock Weather | `get_weather` | Returns mock weather data for a city |
| Reverse String | `reverse_string` | Reverses the characters in a string |

---

## Prerequisites

- Python 3.10+
- pip

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Running the Server

```bash
python main.py
```

The server starts at `http://localhost:8000`.

| URL | Description |
|---|---|
| `http://localhost:8000/docs` | Interactive Swagger UI |
| `http://localhost:8000/redoc` | ReDoc API docs |
| `http://localhost:8000/mcp` | MCP endpoint |

---

## Example API Calls

**Greet a user**
```
GET http://localhost:8000/greet?name=Alice
```
```json
{ "message": "Hello, Alice! Welcome to the Demo MCP Server." }
```

**Calculate**
```
GET http://localhost:8000/calculate?a=10&b=3&operation=multiply
```
```json
{ "a": 10, "b": 3, "operation": "multiply", "result": 30 }
```

**Get Weather**
```
GET http://localhost:8000/weather?city=Tokyo
```
```json
{ "city": "Tokyo", "temp_c": 22, "condition": "Sunny", "humidity": 55 }
```

**Reverse a String**
```
GET http://localhost:8000/reverse?text=hello
```
```json
{ "original": "hello", "reversed": "olleh" }
```

---

## Connecting an MCP Client

Add the following to your MCP client config (e.g. VS Code or Claude Desktop):

```json
{
  "mcpServers": {
    "demo": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `fastapi-mcp` | Converts FastAPI routes into MCP tools |
| `uvicorn` | ASGI server to run the FastAPI app |
