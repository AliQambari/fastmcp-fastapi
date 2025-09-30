# FastAPI + MCP Server Examples

This repository demonstrates two different approaches to creating MCP (Model Context Protocol) servers in Python:

1. **FastAPI-MCP** (`fastapimcp.py`) - A hybrid server that works as both a FastAPI web application AND an MCP server
2. **FastMCP** (`fastmcp.py`) - A standalone MCP server using FastMCP v2

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- pip or uv package manager

### Installationg

1. Clone this repository:
```bash
git clone <your-repo-url>
cd fmcp
```

2. Install dependencies:
```bash
pip install -e .
```

Or using uv:
```bash
uv sync
```

## 📋 Available Tools

Both implementations provide the same core functionality:

- **Sum Numbers** - Add two integers
- **Greet User** - Generate personalized greetings  
- **Translate Text** - Translate text between languages using Google Translate
- **Weather Alerts** - Get active weather alerts for US states

## 🔧 Usage

### Option 1: FastAPI-MCP (Hybrid Server)

The `fastapimcp.py` file creates a server that works as **both** a web API and MCP server simultaneously.

#### Run as Web API:
```bash
python fastapimcp.py
```
- Access web interface: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- MCP endpoint: http://127.0.0.1:8000/mcp

#### Test API endpoints:
```bash
# Sum two numbers
curl -X POST "http://127.0.0.1:8000/sum" \
  -H "Content-Type: application/json" \
  -d '{"a": 5, "b": 3}'

# Greet user
curl -X POST "http://127.0.0.1:8000/greet" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'

# Translate text
curl -X POST "http://127.0.0.1:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "target_lang": "es"}'

# Get weather alerts
curl -X POST "http://127.0.0.1:8000/alerts" \
  -H "Content-Type: application/json" \
  -d '{"state": "CA"}'
```

#### Use as MCP Server:
Connect MCP clients to: `http://127.0.0.1:8000/mcp`

### Option 2: FastMCP (Standalone MCP Server)

The `fastmcp.py` file creates a dedicated MCP server using FastMCP v2.

#### Run MCP Server:
```bash
python fastmcp.py
```

The server will start on `http://127.0.0.1:8000` and provide MCP protocol endpoints.

## 🏗️ Architecture

### FastAPI-MCP Architecture
```
┌─────────────────┐    ┌──────────────────┐
│   FastAPI App   │────│  HTTP Endpoints  │
│                 │    │  /sum, /greet,   │
│                 │    │  /translate,     │
│                 │    │  /alerts         │
└─────────────────┘    └──────────────────┘
         │
         │
┌─────────────────┐    ┌──────────────────┐
│  FastApiMCP     │────│   MCP Protocol   │
│  Integration    │    │   /mcp/*         │
└─────────────────┘    └──────────────────┘
```

### FastMCP Architecture
```
┌─────────────────┐    ┌──────────────────┐
│   FastMCP v2    │────│   MCP Tools      │
│                 │    │   @mcp.tool()    │
└─────────────────┘    └──────────────────┘
         │
         │
┌─────────────────┐    ┌──────────────────┐
│   Resources     │────│   MCP Protocol   │
│   @mcp.resource │    │   Server         │
└─────────────────┘    └──────────────────┘
```

## 🔌 MCP Client Integration

### Claude Desktop Configuration

Add to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "fastapi-mcp": {
      "command": "python",
      "args": ["path/to/fastapimcp.py"],
      "env": {}
    },
    "fastmcp": {
      "command": "python", 
      "args": ["path/to/fastmcp.py"],
      "env": {}
    }
  }
}
```

### Other MCP Clients

Both servers expose standard MCP protocol endpoints that work with any MCP-compatible client.

## 📁 Project Structure

```
fmcp/
├── fastapimcp.py      # FastAPI + MCP hybrid server
├── fastmcp.py         # Standalone FastMCP v2 server  
├── weather_helper.py  # Weather API utilities
├── pyproject.toml     # Project dependencies
└── README.md          # This file
```

## 🛠️ Key Differences

| Feature | FastAPI-MCP | FastMCP |
|---------|-------------|---------|
| **Web API** | ✅ Full REST API | ❌ MCP only |
| **MCP Server** | ✅ Via integration | ✅ Native |
| **Documentation** | ✅ Swagger/OpenAPI | ❌ MCP schema only |
| **HTTP Endpoints** | ✅ Custom routes | ❌ MCP protocol only |
| **Complexity** | Higher | Lower |
| **Use Case** | Dual-purpose apps | MCP-focused tools |

## 🔍 Learning Resources

### Understanding FastAPI-MCP
- Combines FastAPI's web framework with MCP capabilities
- Automatically converts FastAPI routes to MCP tools
- Useful when you need both web API and MCP functionality

### Understanding FastMCP v2
- Purpose-built for MCP protocol
- Simpler decorator-based approach
- Supports both tools and resources
- Ideal for dedicated MCP servers

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in the respective files
2. **Missing dependencies**: Run `pip install -e .` to install all requirements
3. **Weather API errors**: The NWS API requires a proper User-Agent header (already configured)
4. **Translation errors**: Ensure internet connection for Google Translate API

### Debug Mode

Add debug logging to either server:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 License

This project is provided as-is for educational and demonstration purposes.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!