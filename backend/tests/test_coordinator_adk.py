import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.genai.types import Content
from adk_agents.coordinator_agent import coordinator_agent
from services.db import fetch_pipeline_run

# test input (use the normalized sample you already have)
EXP_FILE = "examples/sample_custom_experiment_normalized.json"

with open(EXP_FILE) as f:
    exp = json.load(f)

payload_text = json.dumps(exp)
resp = coordinator_agent(Content(parts=[{"text": payload_text}]))

# print raw ADK response
print("\n=== COORDINATOR RAW RESPONSE ===")
print(resp)

# print textual JSON
try:
    text = resp.candidates[0].content.parts[0].text
    print("\n=== COORDINATOR REPORT ===")
    print(text)
except Exception as e:
    print("Could not extract text:", e)

# fetch from DB to verify persistence
db_path = os.getenv("DATABASE_PATH", "memory/testlab.db")
run = fetch_pipeline_run(db_path, exp.get("run_id"))
print("\n=== FETCHED FROM DB ===")
print(run)
