"""
Coordinator Agent (Enterprise-level)
Orchestrates: Ingest -> Evaluation -> Diagnosis -> Planner
Logs the final report into SQLite DB at memory/testlab.db
Returns an ADK-compliant GenerateContentResponse containing the unified report.
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict

from dotenv import load_dotenv
from google.genai.types import Content, GenerateContentResponse

# Import the agents (assumes these modules exist and are ADK-compatible)
from adk_agents.ingest_agent import ingest_agent
from adk_agents.eval_agent import eval_agent
from adk_agents.diagnosis_agent import diagnosis_agent
from adk_agents.planner_agent import planner_agent

# DB helper
from services.db import init_db, insert_pipeline_run

load_dotenv()

# Ensure DB exists and tables are created
DB_PATH = os.getenv("DATABASE_PATH", "memory/testlab.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
init_db(DB_PATH)


# -------------------------
# ADK Response helper
# -------------------------
def respond(obj: Any) -> GenerateContentResponse:
    """
    Wrap JSON/text into ADK-compliant GenerateContentResponse.
    """
    text = json.dumps(obj, indent=2)
    return GenerateContentResponse(candidates=[{"content": Content(parts=[{"text": text}])}])


# -------------------------
# Utilities
# -------------------------
def extract_text_from_response(resp) -> str:
    """Safely extract the textual content from an ADK response object."""
    try:
        return resp.candidates[0].content.parts[0].text
    except Exception:
        # fallback: try str(resp)
        return str(resp)


def try_parse_json_from_text(text: str):
    """
    Attempt to parse JSON substring from text. Finds first '{' and last '}'.
    Returns dict or None.
    """
    if not text:
        return None
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end+1])
    except Exception:
        return None


# -------------------------
# Coordinator entrypoint
# -------------------------
def coordinator_agent(request: Content) -> GenerateContentResponse:
    """
    Orchestrate the pipeline.

    Input:
      Content.parts[0].text should contain the raw experiment JSON (either ML format
      or custom). We will pass it to the Ingest agent, then Eval, Diagn, Planner.

    Output:
      ADK GenerateContentResponse with the final unified report (and saved to DB).
    """
    ts_start = datetime.utcnow().isoformat() + "Z"
    try:
        raw_text = request.parts[0].text
        raw_input = json.loads(raw_text)

        pipeline_report: Dict[str, Any] = {
            "run_id": raw_input.get("run_id", raw_input.get("experiment_id", "unknown")),
            "timestamps": {"start": ts_start},
            "ingest": None,
            "evaluation": None,
            "diagnosis": None,
            "planner": None,
            "errors": []
        }

        # ---- Step 1: Ingest ----
        try:
            ingest_resp = ingest_agent(Content(parts=[{"text": raw_text}]))
            ingest_text = extract_text_from_response(ingest_resp)
            # try to parse a normalized JSON from ingest output
            normalized = try_parse_json_from_text(ingest_text)
            if normalized:
                pipeline_report["ingest"] = {"status": "ok", "raw": ingest_text, "normalized": normalized}
                normalized_input = normalized
            else:
                # If ingest didn't return normalized JSON, assume input is normalized or use original input
                pipeline_report["ingest"] = {"status": "ok", "raw": ingest_text, "normalized": raw_input}
                normalized_input = raw_input
        except Exception as e:
            pipeline_report["ingest"] = {"status": "error", "error": str(e)}
            pipeline_report["errors"].append({"stage": "ingest", "error": str(e)})
            # proceed with raw input
            normalized_input = raw_input

        # ---- Step 2: Evaluation ----
        try:
            eval_payload_text = json.dumps(normalized_input)
            eval_resp = eval_agent(Content(parts=[{"text": eval_payload_text}]))
            eval_text = extract_text_from_response(eval_resp)
            eval_json = try_parse_json_from_text(eval_text)
            pipeline_report["evaluation"] = {"status": "ok", "raw": eval_text, "parsed": eval_json}
        except Exception as e:
            pipeline_report["evaluation"] = {"status": "error", "error": str(e)}
            pipeline_report["errors"].append({"stage": "evaluation", "error": str(e)})

        # ---- Step 3: Diagnosis ----
        try:
            # pass normalized + optionally baseline (not implemented yet)
            diag_payload = {"normalized": normalized_input}
            diag_text_in = json.dumps(diag_payload)
            diag_resp = diagnosis_agent(Content(parts=[{"text": diag_text_in}]))
            diag_text = extract_text_from_response(diag_resp)
            diag_json = try_parse_json_from_text(diag_text)
            pipeline_report["diagnosis"] = {"status": "ok", "raw": diag_text, "parsed": diag_json}
        except Exception as e:
            pipeline_report["diagnosis"] = {"status": "error", "error": str(e)}
            pipeline_report["errors"].append({"stage": "diagnosis", "error": str(e)})

        # ---- Step 4: Planner / Improvement ----
        try:
            planner_payload = {"normalized": normalized_input}
            # attach parsed diagnosis if available
            if pipeline_report["diagnosis"] and pipeline_report["diagnosis"].get("parsed"):
                planner_payload["diagnosis"] = pipeline_report["diagnosis"]["parsed"]
            planner_resp = planner_agent(Content(parts=[{"text": json.dumps(planner_payload)}]))
            planner_text = extract_text_from_response(planner_resp)
            planner_json = try_parse_json_from_text(planner_text)
            pipeline_report["planner"] = {"status": "ok", "raw": planner_text, "parsed": planner_json}
        except Exception as e:
            pipeline_report["planner"] = {"status": "error", "error": str(e)}
            pipeline_report["errors"].append({"stage": "planner", "error": str(e)})

        # ---- finalize report ----
        ts_end = datetime.utcnow().isoformat() + "Z"
        pipeline_report["timestamps"]["end"] = ts_end

        # Persist to SQLite DB
        try:
            insert_pipeline_run(DB_PATH, pipeline_report["run_id"], pipeline_report)
            pipeline_report["storage"] = {"db": DB_PATH, "status": "saved"}
        except Exception as e:
            pipeline_report["storage"] = {"db": DB_PATH, "status": "error", "error": str(e)}
            pipeline_report["errors"].append({"stage": "storage", "error": str(e)})

        # Return the final pipeline report as ADK response
        return respond(pipeline_report)

    except Exception as e:
        err = {"error": str(e)}
        return respond(err)
