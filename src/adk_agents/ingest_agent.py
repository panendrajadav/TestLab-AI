import json
import os
from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import Content, GenerateContentResponse

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("ERROR: GOOGLE_API_KEY missing in .env")

client = Client(api_key=API_KEY)

ML_REQUIRED = ["run_id", "model", "hyperparameters", "metrics", "timestamp"]

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

def ingest_agent(request: Content) -> GenerateContentResponse:
    try:
        exp_text = request.parts[0].text
        data = json.loads(exp_text)

        # CASE 1: ML format
        if is_ml_format(data):
            print("Detected ML format")
            return GenerateContentResponse(
                output="[SUCCESS] ML experiment validated and ingested."
            )

        # CASE 2: Custom format
        if is_custom_format(data):
            print("Detected CUSTOM format")
            normalized = normalize_custom_format(data)
            return GenerateContentResponse(
                output="[SUCCESS] Custom format normalized:\n"
                       + json.dumps(normalized, indent=2)
            )

        # CASE 3: Unknown
        return GenerateContentResponse(
            output="[ERROR] Unsupported experiment format."
        )

    except Exception as e:
        return GenerateContentResponse(
            output=f"[ERROR] Ingestion failed: {str(e)}"
        )
