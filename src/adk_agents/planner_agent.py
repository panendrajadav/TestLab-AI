"""
Planner / Improvement Agent (Hybrid)
- Rule-based suggestions + optional Gemini LLM plan expansion
- ADK-compliant response (GenerateContentResponse)
"""

import json
import os
from dotenv import load_dotenv
from typing import Dict, Any, List
from google.genai import Client
from google.genai.types import Content, GenerateContentResponse

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY", None)

# create client if API key present (used optionally)
client = None
if API_KEY:
    try:
        client = Client(api_key=API_KEY)
    except Exception:
        client = None  # safe fallback if client cannot be created

# ---------- helpers ----------
def respond(text: str) -> GenerateContentResponse:
    return GenerateContentResponse(candidates=[{"content": Content(parts=[{"text": text}])}])

def rule_based_suggestions(exp: Dict[str, Any], diagnosis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Produce concise rule-based actions based on diagnosis flags and metrics.
    Returns list of suggestion dicts with type, priority (1-high..3-low), and short reason.
    """
    suggestions = []
    flags = diagnosis.get("flags", []) if diagnosis else []
    metrics = exp.get("metrics", {})

    # Example suggestions based on flags
    for f in flags:
        lf = f.lower()
        if "overfit" in lf:
            suggestions.append({
                "action": "Reduce overfitting",
                "priority": 1,
                "details": "Increase regularization (dropout), early stopping; augment data; reduce model capacity.",
                "reason": f
            })
        elif "underfit" in lf:
            suggestions.append({
                "action": "Reduce underfitting / increase capacity",
                "priority": 1,
                "details": "Increase model capacity, train longer, or tune optimizer (learning rate).",
                "reason": f
            })
        elif "unstable_metric" in lf or "unstable" in lf:
            suggestions.append({
                "action": "Stabilize training",
                "priority": 1,
                "details": "Reduce learning rate, increase batch size or add gradient clipping; check data pipeline randomness.",
                "reason": f
            })
        elif "fail_rate" in lf:
            suggestions.append({
                "action": "Inspect failing tests",
                "priority": 1,
                "details": "Group failing tests, reproduce failures locally and prioritize fixes; create focused unit tests.",
                "reason": f
            })
        elif "regression" in lf:
            suggestions.append({
                "action": "Investigate regression",
                "priority": 1,
                "details": "Compare checkpoints, run A/B test with previous config, and roll back if necessary.",
                "reason": f
            })

    # Generic suggestions derived from metrics if no flags
    if not suggestions:
        # If accuracy present but low -> tune LR
        acc = metrics.get("accuracy") or metrics.get("success_rate")
        if acc is not None:
            if acc < 0.6:
                suggestions.append({
                    "action": "Aggressive tuning",
                    "priority": 1,
                    "details": "Try larger model, longer training, and LR sweep (log scale).",
                    "reason": f"low primary metric: {acc}"
                })
            elif acc < 0.8:
                suggestions.append({
                    "action": "Moderate tuning",
                    "priority": 2,
                    "details": "Run small hyperparameter sweep over LR and batch size.",
                    "reason": f"medium primary metric: {acc}"
                })
            else:
                suggestions.append({
                    "action": "Fine-tuning",
                    "priority": 3,
                    "details": "Small hyperparameter tuning and more data augmentation.",
                    "reason": f"high primary metric: {acc}"
                })
        else:
            # fallback generic plan
            suggestions.append({
                "action": "Gather more signal",
                "priority": 2,
                "details": "Collect more runs, add validation splits, and establish baseline metrics.",
                "reason": "no primary metric available"
            })

    # Deduplicate suggestions by action
    unique = {}
    for s in suggestions:
        key = s["action"]
        if key not in unique or s["priority"] < unique[key]["priority"]:
            unique[key] = s
    return list(unique.values())

def llm_generate_plan(exp: Dict[str, Any], diagnosis: Dict[str, Any], suggestions: List[Dict[str, Any]]) -> str:
    """
    Use Gemini (via google-genai Client) to expand suggestions into a prioritized plan.
    If Client is not available, return a human-readable fallback string.
    """
    prompt = {
        "title": "TestLab AI - Improvement Plan Generator",
        "context": {
            "run_id": exp.get("run_id"),
            "metrics": exp.get("metrics"),
            "diagnosis": diagnosis,
            "suggestions": suggestions
        },
        "instructions": (
            "Produce a concise, prioritized improvement plan (max 300 words) with 3 sections:\n"
            "1) Immediate actions (what to change now)\n"
            "2) Medium-term experiments (hyperparameter sweeps, data work)\n"
            "3) Long-term suggestions (architecture / dataset changes)\n"
            "Be concrete: include example hyperparameter values (learning rate, batch_size, epochs) when relevant."
        )
    }

    prompt_text = json.dumps(prompt, indent=2)

    # If LLM client is unavailable, return fallback
    if client is None:
        fallback = "LLM not available — fallback plan:\n"
        for s in suggestions:
            fallback += f"- {s['action']} (priority {s['priority']}): {s['details']}\n"
        return fallback

    # Try to call Gemini (best-effort). If it fails, return fallback text.
    try:
        # NOTE: different google-genai versions expose different methods.
        # We'll use the high-level `client.generate_text` if available, otherwise fall back.
        # Adjust model name as desired via environment (e.g., MODEL_NAME).
        model_name = os.getenv("MODEL_NAME", "gemini-1.5-pro")
        # The exact method name may vary by version; attempt common option:
        if hasattr(client, "generate_text"):
            response = client.generate_text(model=model_name, prompt=prompt_text, max_output_tokens=512)
            plan_text = response.text if hasattr(response, "text") else str(response)
        else:
            # try responses API
            if hasattr(client, "responses"):
                resp = client.responses.create(model=model_name, input=prompt_text)
                plan_text = resp.output_text if hasattr(resp, "output_text") else str(resp)
            else:
                plan_text = None

        if not plan_text:
            raise RuntimeError("No text from LLM")

        return plan_text

    except Exception as e:
        # fallback
        fallback = f"LLM call failed ({e}). Fallback plan:\n"
        for s in suggestions:
            fallback += f"- {s['action']} (priority {s['priority']}): {s['details']}\n"
        return fallback

# ---------- Agent Entrypoint ----------
def planner_agent(request: Content) -> GenerateContentResponse:
    """
    ADK Planner agent entrypoint.
    Expects input either as normalized experiment dict OR a wrapper:
      { "normalized": {...}, "diagnosis": {...} }
    """
    try:
        raw = request.parts[0].text
        data = json.loads(raw)

        exp = data.get("normalized", data)
        diagnosis = data.get("diagnosis", {})

        suggestions = rule_based_suggestions(exp, diagnosis)
        plan_text = llm_generate_plan(exp, diagnosis, suggestions)

        output = {
            "run_id": exp.get("run_id"),
            "suggestions": suggestions,
            "llm_plan": plan_text
        }

        return respond(json.dumps(output, indent=2))

    except Exception as e:
        return respond(json.dumps({"error": str(e)}))
