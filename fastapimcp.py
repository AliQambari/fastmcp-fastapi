
######################\
#using FastApiMCP
######################3

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi_mcp import FastApiMCP
from weather_helper import make_nws_request, format_alert
import asyncio
from deep_translator import GoogleTranslator

app = FastAPI()

# Request body schemas
class SumRequest(BaseModel):
    a: int
    b: int

class GreetRequest(BaseModel):
    name: str

class AlertRequest(BaseModel):
    state: str

class TranslateRequest(BaseModel):
    text: str
    target_lang: str  # e.g., "es" for Spanish, "fr" for French

class QueryRequest(BaseModel):
    query: str

NWS_API_BASE = "https://api.weather.gov"

@app.post("/alerts", operation_id="get_weather_alerts")
async def get_alerts(req: AlertRequest):
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{req.state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return {"alerts": "\n---\n".join(alerts)}

@app.post("/sum",operation_id="sum_numbers")
async def sum_numbers(req: SumRequest):
    """
    Returns the sum of two numbers.

    Parameters:
    req (SumRequest): Request body containing two numbers to be added.

    Returns:
        dict: Response containing the sum of the two numbers.
    """
    return {"sum": req.a + req.b}

@app.post("/greet",operation_id="greet_user")
async def greet(req: GreetRequest):
    """
    Returns a greeting message for a given name.

    Parameters:
    req (GreetRequest): Request body containing the name to be greeted.

    Returns:
        dict: Response containing the greeting message.
    """
    return {"message": f"Hello (ADDITIONAL NONSENSE TO SEE IF IT WORKS!:), {req.name}!"}


@app.post("/translate",operation_id="translate_text")   #add operation id for the MCP
async def translate_text(req: TranslateRequest):
    """
    Translate text from one language to another.

    Parameters:
    req (TranslateRequest): Request body containing the text to be translated and the target language.

    Returns:
        dict: Response containing the translated text, the original text, and the target language.
    """
    loop = asyncio.get_running_loop()
    
    # Wrap synchronous translator in thread
    translated_text = await loop.run_in_executor(
        None, lambda: GoogleTranslator(source='auto', target=req.target_lang).translate(req.text)
    )
    
    return {
        "original": req.text,
        "translated": translated_text,
        "target_lang": req.target_lang
    }



#create MCP AFTER routes exist
mcp = FastApiMCP(
    app,
    name="fastapi-MCP",
    description="MCP server",
    describe_all_responses=True,
    describe_full_response_schema=True
)

"""
mcp = FastApiMCP(
    app,
    include_operations=["translate", "greet"]
)
# exclude_operations 
"""
mcp.mount_http()
# Refresh the MCP server to include the new endpoint
mcp.setup_server()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)