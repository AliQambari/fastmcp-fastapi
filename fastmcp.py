######################\
#using FastMCP v2.0
######################3



import asyncio
from deep_translator import GoogleTranslator
from weather_helper import make_nws_request, format_alert
from fastmcp import FastMCP

# -----------------------
# Initialize FastMCP
# -----------------------
mcp = FastMCP(name="MyFastMCP")

# -----------------------
# Tools
# -----------------------

@mcp.tool()
def sum_numbers(a: int, b: int) -> dict:
    """Return the sum of two numbers"""
    return {"sum": a + b}

@mcp.tool()
def greet_user(name: str) -> dict:
    """Return a greeting message"""
    return {"message": f"Hello (ADDITIONAL NONSENSE TO SEE IF IT WORKS!:), {name}!"}

@mcp.tool()
async def translate_text(text: str, target_lang: str) -> dict:
    """Translate text from one language to another"""
    loop = asyncio.get_running_loop()
    translated = await loop.run_in_executor(
        None, lambda: GoogleTranslator(source="auto", target=target_lang).translate(text)
    )
    return {
        "original": text,
        "translated": translated,
        "target_lang": target_lang,
    }

@mcp.tool()
async def get_weather_alerts(state: str) -> dict:
    """Get active weather alerts for a US state"""
    url = f"https://api.weather.gov/alerts/active/area/{state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return {"alerts": "Unable to fetch alerts or no alerts found."}
    if not data["features"]:
        return {"alerts": "No active alerts for this state."}
    alerts = [format_alert(f) for f in data["features"]]
    return {"alerts": "\n---\n".join(alerts)}

# -----------------------
# Resources
# -----------------------

@mcp.resource("resource://ali_age")
def get_ali_age() -> dict:
    """Provides Ali’s age as a static resource"""
    return {"age": 15}


@mcp.tool()
def goodbye_user(name: str) -> dict:
    """Return a greeting message"""
    return {"message": f"goodbye (ADDITIONAL NONSENSE TO SEE IF IT WORKS!:), {name}!"}


@mcp.resource("resource://weather://{state}/alerts")
async def resource_weather_alerts(state: str) -> dict:
    """Expose alerts as a resource per state"""
    url = f"https://api.weather.gov/alerts/active/area/{state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return {"alerts": "Unable to fetch alerts or no alerts found."}
    if not data["features"]:
        return {"alerts": "No active alerts for this state."}
    alerts = [format_alert(f) for f in data["features"]]
    return {"alerts": "\n---\n".join(alerts)}

# -----------------------
# Run the MCP server
# -----------------------
if __name__ == "__main__":
    print("Starting FastMCP server on http://127.0.0.1:8000")
    mcp.run(transport="streamable-http")
