import json
import os
from dotenv import load_dotenv
try:
    import google.generativeai as genai
    from google.genai.types import Content, GenerateContentResponse, Part
except ImportError:
    genai = None
    Content = dict
    GenerateContentResponse = dict
    Part = dict

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("ERROR: GOOGLE_API_KEY missing in .env")

# Configure Gemini
if genai:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-pro")
else:
    model = None

ML_REQUIRED = ["run_id", "model", "hyperparameters", "metrics", "timestamp"]

def adk_response(text: str):
    """ADK-compliant response wrapper"""
    if genai:
        return GenerateContentResponse(
            candidates=[{
                "content": Content(parts=[Part(text=text)])
            }]
        )
    else:
        return {"candidates": [{"content": {"parts": [{"text": text}]}}]}

def is_ml_format(data: dict):
    return all(f in data for f in ML_REQUIRED)

def is_custom_format(data: dict):
    return (
        "experiment_id" in data
        and "results" in data
        and "status" in data
    )

def normalize_custom_format(data: dict):
    return {
        "run_id": data.get("experiment_id"),
        "model": data.get("name", "unknown_model"),
        "hyperparameters": {
            "description": data.get("description", "N/A")
        },
        "metrics": data.get("results", {}),
        "timestamp": data.get("created_at", "1970-01-01T00:00:00Z")
    }

def ingest_agent(request) -> GenerateContentResponse:
    try:
        # Handle both dict and Content object inputs
        if isinstance(request, dict):
            data = request
        elif hasattr(request, 'parts'):
            exp_text = request.parts[0].text
            data = json.loads(exp_text)
        else:
            data = json.loads(str(request))

        # CASE 1: ML format
        if is_ml_format(data):
            result = {
                "status": "success",
                "format": "ml",
                "normalized": data,
                "message": "ML experiment validated and ingested."
            }
            return adk_response(json.dumps(result, indent=2))

        # CASE 2: Custom format
        if is_custom_format(data):
            normalized = normalize_custom_format(data)
            result = {
                "status": "success",
                "format": "custom",
                "normalized": normalized,
                "message": "Custom format normalized and ingested."
            }
            return adk_response(json.dumps(result, indent=2))

        # CASE 3: Unknown
        error_result = {
            "status": "error",
            "message": "Unsupported experiment format.",
            "received_keys": list(data.keys()) if isinstance(data, dict) else "non-dict"
        }
        return adk_response(json.dumps(error_result, indent=2))

    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Ingestion failed: {str(e)}"
        }
        return adk_response(json.dumps(error_result, indent=2))