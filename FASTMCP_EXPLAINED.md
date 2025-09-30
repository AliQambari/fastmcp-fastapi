# FastMCP v2 Implementation Deep Dive

This document explains how the `fastmcp.py` implementation works and the core concepts of FastMCP v2 for building dedicated MCP servers.

## 🏗️ How It Works

### 1. FastMCP Initialization

The server starts with a simple FastMCP instance:

```python
from fastmcp import FastMCP
mcp = FastMCP(name="MyFastMCP")
```

**Key Point**: This creates a dedicated MCP server, not a web application.

### 2. Tool Definitions

Tools are defined using the `@mcp.tool()` decorator:

```python
@mcp.tool()
def sum_numbers(a: int, b: int) -> dict:
    """Return the sum of two numbers"""
    return {"sum": a + b}
```

### 3. Async Tool Support

FastMCP v2 natively supports async operations:

```python
@mcp.tool()
async def translate_text(text: str, target_lang: str) -> dict:
    """Translate text from one language to another"""
    loop = asyncio.get_running_loop()
    translated = await loop.run_in_executor(
        None, lambda: GoogleTranslator(source="auto", target=target_lang).translate(text)
    )
    return {"original": text, "translated": translated, "target_lang": target_lang}
```

### 4. Resource Definitions

FastMCP v2 supports resources in addition to tools:

```python
@mcp.resource("resource://ali_age")
def get_ali_age() -> dict:
    """Provides Ali's age as a static resource"""
    return {"age": 15}

@mcp.resource("resource://weather://{state}/alerts")
async def resource_weather_alerts(state: str) -> dict:
    """Expose alerts as a resource per state"""
    # Implementation here
```

### 5. Server Execution

```python
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

## 🔄 MCP Protocol Flow

### Tool Execution:
```
MCP Client → FastMCP Server → Tool Function → Response → MCP Client
```

### Resource Access:
```
MCP Client → FastMCP Server → Resource Function → Data → MCP Client
```

## 🎯 Key Benefits

### 1. **Purpose-Built for MCP**
- Native MCP protocol support
- No HTTP overhead for non-MCP use cases
- Optimized for AI agent interactions

### 2. **Simple Decorator Pattern**
- Clean, intuitive API
- Minimal boilerplate code
- Easy to understand and maintain

### 3. **Built-in Resource Support**
- Static and dynamic resources
- URI-based resource addressing
- Parameterized resource paths

### 4. **Type Safety**
- Full type hint support
- Automatic parameter validation
- Rich error messages

## ⚙️ Core Concepts

### 1. **Tools vs Resources**

**Tools** are functions that perform actions:
```python
@mcp.tool()
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
    """Calculate distance between two points"""
    # Performs calculation
    return {"distance_km": result}
```

**Resources** provide data or content:
```python
@mcp.resource("resource://config/settings")
def get_settings() -> dict:
    """Provides application configuration"""
    return {"api_version": "1.0", "max_requests": 1000}
```

### 2. **Resource URI Patterns**

Static resources:
```python
@mcp.resource("resource://user/profile")
def get_profile() -> dict:
    return {"name": "John", "role": "admin"}
```

Parameterized resources:
```python
@mcp.resource("resource://users/{user_id}/profile")
def get_user_profile(user_id: str) -> dict:
    return {"user_id": user_id, "name": f"User {user_id}"}
```

### 3. **Transport Options**

FastMCP v2 supports multiple transport methods:

```python
# HTTP transport (most common)
mcp.run(transport="streamable-http")

# Standard I/O (for process-based clients)
mcp.run(transport="stdio")


## 🔧 Advanced Patterns

### 1. **Error Handling**

```python
@mcp.tool()
def risky_operation(value: int) -> dict:
    """Demonstrates error handling"""
    if value < 0:
        raise ValueError("Value must be positive")
    
    try:
        result = 100 / value
        return {"result": result}
    except ZeroDivisionError:
        return {"error": "Cannot divide by zero"}
```

### 2. **Complex Data Types**

```python
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class WeatherData:
    temperature: float
    humidity: int
    conditions: str

@mcp.tool()
def get_weather_forecast(days: int) -> dict:
    """Get weather forecast for multiple days"""
    forecast = []
    for i in range(days):
        forecast.append({
            "day": i + 1,
            "temperature": 20 + i,
            "humidity": 60,
            "conditions": "sunny"
        })
    return {"forecast": forecast}
```

### 3. **State Management**

```python
# Global state (use carefully)
_cache = {}

@mcp.tool()
def cache_value(key: str, value: str) -> dict:
    """Store a value in cache"""
    _cache[key] = value
    return {"cached": True, "key": key}

@mcp.tool()
def get_cached_value(key: str) -> dict:
    """Retrieve a value from cache"""
    value = _cache.get(key)
    return {"key": key, "value": value, "found": value is not None}
```

### 4. **External API Integration**

```python
import httpx

@mcp.tool()
async def fetch_api_data(endpoint: str) -> dict:
    """Fetch data from external API"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://api.example.com/{endpoint}")
            response.raise_for_status()
            return {"data": response.json(), "status": "success"}
        except httpx.HTTPError as e:
            return {"error": str(e), "status": "failed"}
```

## 🚨 Important Considerations

### 1. **Function Signatures**
All parameters must be JSON-serializable types:

```python
# ✅ Good
@mcp.tool()
def good_function(name: str, age: int, active: bool) -> dict:
    pass

# ❌ Problematic
@mcp.tool()
def bad_function(obj: SomeCustomClass) -> dict:  # Custom classes not supported
    pass
```

### 2. **Return Values**
Always return JSON-serializable data:

```python
# ✅ Good
return {"result": [1, 2, 3], "status": "ok"}

# ❌ Problematic  
return SomeCustomObject()  # Unless properly serializable
```

### 3. **Resource URI Uniqueness**
Each resource must have a unique URI:

```python
# ❌ Conflict
@mcp.resource("resource://data")
def get_data1(): pass

@mcp.resource("resource://data")  # Same URI!
def get_data2(): pass
```

## 🎓 Best Practices

### 1. **Descriptive Function Names**
Function names become tool names in MCP:

```python
# ✅ Good - clear purpose
@mcp.tool()
def calculate_mortgage_payment(principal: float, rate: float, years: int):
    pass

# ❌ Avoid - unclear purpose
@mcp.tool()
def calc(a: float, b: float, c: int):
    pass
```

### 2. **Comprehensive Docstrings**
Docstrings become tool descriptions:

```python
@mcp.tool()
def translate_text(text: str, target_lang: str) -> dict:
    """
    Translate text from one language to another using Google Translate.
    
    Args:
        text: The text to translate
        target_lang: Target language code (e.g., 'es' for Spanish, 'fr' for French)
        
    Returns:
        Dictionary containing original text, translated text, and target language
    """
```

### 3. **Consistent Return Formats**
Use consistent response structures:

```python
# ✅ Consistent success format
def success_response(data):
    return {"success": True, "data": data, "timestamp": time.time()}

# ✅ Consistent error format  
def error_response(message):
    return {"success": False, "error": message, "timestamp": time.time()}
```

### 4. **Resource Organization**
Use hierarchical URI patterns:

```python
# ✅ Well-organized
@mcp.resource("resource://app/config/database")
@mcp.resource("resource://app/config/api")
@mcp.resource("resource://app/users/{id}/profile")
@mcp.resource("resource://app/users/{id}/settings")
```

## 🔍 Debugging Tips

### 1. **Enable Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. **Test Tools Individually**
```python
# Test tools directly before running server
if __name__ == "__main__":
    # Test a tool
    result = sum_numbers(5, 3)
    print(f"Sum result: {result}")
    
    # Then run server
    mcp.run(transport="streamable-http")
```

### 3. **Validate Resource URIs**
```python
# Check resource registration
print("Registered resources:")
for resource in mcp._resources:
    print(f"  {resource}")
```

## 🚀 Performance Considerations

### 1. **Async for I/O Operations**
Always use async for network/file operations:

```python
# ✅ Good - non-blocking
@mcp.tool()
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ❌ Avoid - blocking
@mcp.tool()
def fetch_data_sync(url: str) -> dict:
    import requests
    response = requests.get(url)  # Blocks the event loop
    return response.json()
```

### 2. **Resource Caching**
Cache expensive resource computations:

```python
from functools import lru_cache

@mcp.resource("resource://expensive/computation")
@lru_cache(maxsize=128)
def expensive_resource() -> dict:
    # Expensive computation here
    return {"result": "computed_value"}
```

FastMCP v2 provides a clean, efficient way to build MCP servers with minimal overhead and maximum flexibility for AI agent interactions.