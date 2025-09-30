# FastAPI-MCP Implementation Deep Dive

This document explains how the `fastapimcp.py` implementation works and the key concepts behind combining FastAPI with MCP.

## 🏗️ How It Works

### 1. Standard FastAPI Application

The file starts as a regular FastAPI application:

```python
from fastapi import FastAPI
app = FastAPI()
```

### 2. Pydantic Request Models

Each endpoint uses Pydantic models for request validation:

```python
class SumRequest(BaseModel):
    a: int
    b: int

class TranslateRequest(BaseModel):
    text: str
    target_lang: str
```

**Why this matters**: These models provide automatic validation, documentation, and type safety.

### 3. FastAPI Route Definitions

Standard FastAPI routes with `operation_id` parameters:

```python
@app.post("/sum", operation_id="sum_numbers")
async def sum_numbers(req: SumRequest):
    """Returns the sum of two numbers."""
    return {"sum": req.a + req.b}
```

**Key Point**: The `operation_id` parameter is crucial - it becomes the MCP tool name.

### 4. MCP Integration Layer

After defining all routes, the MCP integration is added:

```python
mcp = FastApiMCP(
    app,
    name="fastapi-MCP",
    description="MCP server",
    describe_all_responses=True,
    describe_full_response_schema=True
)
```

### 5. Mounting and Setup

```python
mcp.mount_http()  # Mounts MCP endpoints on /mcp/*
mcp.setup_server()  # Configures the MCP server
```

## 🔄 Request Flow

### As Web API:
```
HTTP Request → FastAPI Route → Pydantic Validation → Business Logic → JSON Response
```

### As MCP Server:
```
MCP Request → FastApiMCP → FastAPI Route → Pydantic Validation → Business Logic → MCP Response
```

## 🎯 Key Benefits

### 1. **Dual Functionality**
- Same code serves both web clients and MCP clients
- No duplication of business logic
- Consistent behavior across protocols

### 2. **Automatic Documentation**
- FastAPI generates OpenAPI/Swagger docs
- MCP schema is auto-generated from FastAPI routes
- Type hints provide rich documentation

### 3. **Validation & Error Handling**
- Pydantic models ensure data integrity
- FastAPI's exception handling works for both protocols
- Consistent error responses

### 4. **Development Experience**
- Use FastAPI's development server with hot reload
- Test endpoints via Swagger UI
- Debug with standard FastAPI tools

## ⚙️ Configuration Options

### Include/Exclude Operations

```python
# Only expose specific operations to MCP
mcp = FastApiMCP(
    app,
    include_operations=["translate_text", "greet_user"]
)

# Exclude specific operations from MCP
mcp = FastApiMCP(
    app,
    exclude_operations=["internal_admin_endpoint"]
)
```

### Response Schema Control

```python
mcp = FastApiMCP(
    app,
    describe_all_responses=True,        # Include response schemas
    describe_full_response_schema=True  # Full schema details
)
```

## 🔧 Advanced Patterns

### 1. **Async Operations**
Both sync and async endpoints work seamlessly:

```python
@app.post("/translate", operation_id="translate_text")
async def translate_text(req: TranslateRequest):
    # Async operation using executor for sync libraries
    loop = asyncio.get_running_loop()
    translated = await loop.run_in_executor(
        None, lambda: GoogleTranslator(...).translate(req.text)
    )
    return {"translated": translated}
```

### 2. **Error Handling**
FastAPI's exception handling works for both protocols:

```python
from fastapi import HTTPException

@app.post("/risky-operation")
async def risky_operation():
    if something_wrong:
        raise HTTPException(status_code=400, detail="Something went wrong")
```

### 3. **Dependency Injection**
FastAPI dependencies work normally:

```python
from fastapi import Depends

def get_api_key(api_key: str = Header(...)):
    return api_key

@app.post("/protected", operation_id="protected_operation")
async def protected_endpoint(api_key: str = Depends(get_api_key)):
    return {"message": "Access granted"}
```

## 🚨 Important Considerations

### 1. **Operation IDs are Required**
Without `operation_id`, endpoints won't be exposed to MCP:

```python
# ❌ Won't work for MCP
@app.post("/endpoint")
async def my_endpoint():
    pass

# ✅ Works for MCP  
@app.post("/endpoint", operation_id="my_tool")
async def my_endpoint():
    pass
```

### 2. **Request Body Structure**
MCP calls use the Pydantic model structure:

```python
# FastAPI endpoint expects:
{"a": 5, "b": 3}

# MCP tool call uses same structure:
mcp_client.call_tool("sum_numbers", {"a": 5, "b": 3})
```

### 3. **Response Format**
Responses should be JSON-serializable:

```python
# ✅ Good
return {"result": "success", "data": [1, 2, 3]}

# ❌ Problematic
return SomeCustomObject()  # Unless it has proper serialization
```

## 🎓 Best Practices

### 1. **Clear Operation IDs**
Use descriptive, action-oriented names:

```python
# ✅ Good
operation_id="translate_text"
operation_id="get_weather_alerts" 
operation_id="calculate_distance"

# ❌ Avoid
operation_id="endpoint1"
operation_id="handler"
```

### 2. **Comprehensive Docstrings**
MCP uses these for tool descriptions:

```python
@app.post("/translate", operation_id="translate_text")
async def translate_text(req: TranslateRequest):
    """
    Translate text from one language to another using Google Translate.
    
    Supports automatic source language detection and translation to 
    over 100 target languages using ISO 639-1 language codes.
    """
```

### 3. **Structured Responses**
Return consistent, well-structured data:

```python
# ✅ Structured response
return {
    "original": req.text,
    "translated": translated_text,
    "target_lang": req.target_lang,
    "confidence": 0.95
}

# ❌ Inconsistent
return translated_text  # Just a string
```

## 🔍 Debugging Tips

### 1. **Test Both Protocols**
- Use Swagger UI for HTTP testing: `http://localhost:8000/docs`
- Use MCP client for protocol testing: `http://localhost:8000/mcp`

### 2. **Enable Debug Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. **Validate MCP Schema**
Check the generated MCP schema:
```bash
curl http://localhost:8000/mcp/tools/list
```

This dual-protocol approach makes FastAPI-MCP perfect for applications that need to serve both traditional web clients and AI agents through the MCP protocol.