"""
Hybrid Evaluation Agent — supports ML and Test-based metrics
ADK-compliant response (GenerateContentResponse)
"""

import json
import math
import os
from dotenv import load_dotenv
from google.genai.types import Content, GenerateContentResponse

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY", None)

# Thresholds
THRESHOLDS = {
    "accuracy_good": 0.85,
    "accuracy_warning": 0.7,
    "success_rate_good": 0.9,
    "success_rate_warning": 0.7
}

# ------------- Response Helper -------------
def respond(text: str):
    """Proper ADK-compliant response wrapper."""
    return GenerateContentResponse(
        candidates=[
            {
                "content": Content(parts=[{"text": text}])
            }
        ]
    )

# ------------- Metric Helpers -------------
def is_test_metrics(metrics):
    return (
        "success_rate" in metrics
        or ("passed" in metrics and "failed" in metrics and "total_tests" in metrics)
    )

def grade_success_rate(metrics):
    sr = metrics.get("success_rate")

    if sr is None:
        try:
            passed = metrics.get("passed", 0)
            total = metrics.get("total_tests", 0)
            sr = passed / total if total > 0 else None
        except:
            sr = None

    if sr is None:
        return "UNKNOWN", None

    if sr >= THRESHOLDS["success_rate_good"]:
        return "GOOD", sr
    if sr >= THRESHOLDS["success_rate_warning"]:
        return "WARNING", sr
    return "FAIL", sr

def safe_metric(metrics, names):
    for n in names:
        if n in metrics:
            return metrics[n]
    return None

# ------------- Agent Entry -------------
def eval_agent(request) -> GenerateContentResponse:
    try:
        # Handle both dict and Content object inputs
        if isinstance(request, dict):
            exp = request
        elif hasattr(request, 'parts'):
            raw = request.parts[0].text
            exp = json.loads(raw)
        else:
            # Assume it's a JSON string
            exp = json.loads(str(request))

        metrics = exp.get("metrics", {})
        run_id = exp.get("run_id", "unknown")

        # ------------------- TEST METRICS -------------------
        if is_test_metrics(metrics):
            grade, sr = grade_success_rate(metrics)

            notes = []
            if grade == "GOOD":
                notes.append("High success rate. System performing well.")
            elif grade == "WARNING":
                notes.append("Moderate success rate. Needs inspection.")
            elif grade == "FAIL":
                notes.append("Low success rate. System failing tests.")
            else:
                notes.append("Success rate unavailable.")

            output = {
                "run_id": run_id,
                "metric_type": "test_based",
                "grade": grade,
                "success_rate": sr,
                "raw_metrics": metrics,
                "notes": notes
            }

            return respond(json.dumps(output, indent=2))

        # ------------------- ML METRICS -------------------
        accuracy = safe_metric(metrics, ["accuracy", "acc"])
        train_loss = safe_metric(metrics, ["train_loss"])
        val_loss = safe_metric(metrics, ["val_loss"])

        # Accuracy grading
        if accuracy is None:
            grade = "UNKNOWN"
        elif accuracy >= THRESHOLDS["accuracy_good"]:
            grade = "GOOD"
        elif accuracy >= THRESHOLDS["accuracy_warning"]:
            grade = "WARNING"
        else:
            grade = "FAIL"

        output = {
            "run_id": run_id,
            "metric_type": "ml_based",
            "grade": grade,
            "accuracy": accuracy,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "raw_metrics": metrics,
            "notes": [f"ML metric evaluation applied. Grade={grade}"]
        }

        return respond(json.dumps(output, indent=2))

    except Exception as e:
        return respond(json.dumps({"error": str(e)}, indent=2))
