"""
Advanced Diagnosis Agent (ADK-compliant)
- Multi-check anomaly detection
- Produces severity score (0-100), flags, recommended actions
- LLM-ready explanation field (placeholder: can be replaced with Gemini call later)
"""

import json
import math
import os

# Simple response class to replace Google's GenerateContentResponse
class DiagnosisResponse:
    def __init__(self, candidates):
        self.candidates = candidates

# ---------------------------
# Configuration / thresholds
# ---------------------------
TH = {
    # ML thresholds
    "val_over_train_pct_warn": 0.10,   # val_loss > train_loss by 10% -> warning
    "val_over_train_pct_fail": 0.30,   # >30% -> fail / severe
    "train_val_ratio_unstable": 0.20,  # large relative diff triggers instability
    "variance_rel_threshold": 0.08,    # rel stddev level considered high
    # test metric thresholds
    "success_rate_good": 0.90,
    "success_rate_warning": 0.75,
    # severity weights
    "weights": {
        "missing_artifact": 25,
        "high_fail_rate": 30,
        "overfit_warning": 15,
        "overfit_fail": 35,
        "high_variance": 20,
        "low_success_rate": 30,
        "metric_spike": 20,
        "drift_hint": 25
    }
}

# ---------------------------
# Response helper (ADK)
# ---------------------------
def respond(obj):
    text = json.dumps(obj, indent=2)
    return DiagnosisResponse(
        candidates=[
            type('Candidate', (), {
                'content': type('Content', (), {
                    'parts': [type('Part', (), {'text': text})()]
                })()
            })()
        ]
    )

# ---------------------------
# small helpers
# ---------------------------
def safe_get(metrics, keys):
    for k in keys:
        if k in metrics:
            return metrics[k]
    return None

def rel_std(values):
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return float("inf") if any(v != 0 for v in values) else 0.0
    n = len(values)
    if n <= 1:
        return 0.0
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return math.sqrt(var) / abs(mean)

# ---------------------------
# core diagnosis checks
# ---------------------------
def check_missing_artifacts(exp):
    artifacts = exp.get("artifacts", {})
    if not artifacts or not any(artifacts.values()):
        return True, "No artifacts (checkpoint) found."
    return False, None

def check_test_failures(metrics):
    # For test-based metrics compute fail rate
    if "failed" in metrics and "total_tests" in metrics:
        failed = metrics.get("failed", 0)
        total = metrics.get("total_tests", 0)
        if total > 0:
            fail_rate = failed / total
            if fail_rate > 0.2:  # arbitrary threshold -> severe
                return True, f"High fail rate: {failed}/{total} ({fail_rate:.1%})."
            if fail_rate > 0.05:
                return True, f"Moderate fail rate: {failed}/{total} ({fail_rate:.1%})."
    # fallback: check success_rate
    if "success_rate" in metrics:
        sr = metrics.get("success_rate")
        if sr is not None:
            if sr < TH["success_rate_warning"]:
                return True, f"Low success rate: {sr:.2f}."
    return False, None

def check_overfit_underfit(metrics):
    train_loss = safe_get(metrics, ["train_loss"])
    val_loss = safe_get(metrics, ["val_loss", "validation_loss"])
    flags = []
    if train_loss is not None and val_loss is not None:
        # val > train => possible overfit
        if train_loss > 0:
            pct = (val_loss - train_loss) / max(train_loss, 1e-9)
            if pct > TH["val_over_train_pct_fail"]:
                flags.append(("overfit_fail", f"Validation loss is {pct:.1%} higher than training loss (severe overfit)."))
            elif pct > TH["val_over_train_pct_warn"]:
                flags.append(("overfit_warn", f"Validation loss is {pct:.1%} higher than training loss (possible overfit)."))
        # underfit: both losses high / similar, or accuracy low -- handled in eval agent
    return flags

def check_metric_spikes(metrics):
    # detect large sudden changes in history arrays
    spikes = []
    for k, v in metrics.items():
        if isinstance(v, list) and len(v) >= 3:
            # look for sudden change from previous to last > 50%
            prev = v[-2]
            last = v[-1]
            if prev != 0 and abs((last - prev) / max(abs(prev), 1e-9)) > 0.5:
                spikes.append((k, f"Large spike in '{k}' from {prev} -> {last}"))
    return spikes

def check_variance(metrics):
    flags = []
    for k, v in metrics.items():
        if isinstance(v, list) and len(v) >= 3:
            rs = rel_std(v)
            if rs > TH["variance_rel_threshold"]:
                flags.append((k, f"High relative variability in '{k}' (rel_std={rs:.2f})"))
    return flags

def check_drift_hint(exp):
    # Placeholder: if memory/baseline data exists, compare; here we check timestamps to hint drift
    # If a timestamp is old or inconsistent, we just return None — real drift check uses MemoryBank.
    return None  # no-op now; future extension

# ---------------------------
# severity calculator
# ---------------------------
def compute_severity(flags):
    score = 0
    # flags is list of tuples (code or key, message)
    for code, _ in flags:
        w = TH["weights"].get(code, 10)
        score += w
    return min(100, score)

# ---------------------------
# Agent entrypoint
# ---------------------------
def diagnosis_agent(request):
    try:
        # Handle both dict and Content object inputs
        if isinstance(request, dict):
            data = request
        elif hasattr(request, 'parts'):
            raw = request.parts[0].text
            data = json.loads(raw)
        else:
            # Assume it's a JSON string
            data = json.loads(str(request))

        # input normalized experiment dict expected
        exp = data.get("normalized", data)
        metrics = exp.get("metrics", {})

        # accumulate flags (code, message)
        flags = []

        # missing artifacts
        ma, ma_msg = check_missing_artifacts(exp)
        if ma:
            flags.append(("missing_artifact", ma_msg))

        # test failure checks
        tf, tf_msg = check_test_failures(metrics)
        if tf:
            # choose severity code
            if "High fail rate" in (tf_msg or "") or "Low success rate" in (tf_msg or ""):
                flags.append(("high_fail_rate", tf_msg))
            else:
                flags.append(("high_fail_rate", tf_msg))

        # overfit/underfit
        oflags = check_overfit_underfit(metrics)
        for code, msg in oflags:
            if code == "overfit_fail":
                flags.append(("overfit_fail", msg))
            else:
                flags.append(("overfit_warning", msg))

        # spikes
        spikes = check_metric_spikes(metrics)
        for k, msg in spikes:
            flags.append(("metric_spike", msg))

        # variance checks
        var_flags = check_variance(metrics)
        for k, msg in var_flags:
            flags.append(("high_variance", msg))

        # drift hint placeholder
        drift = check_drift_hint(exp)
        if drift:
            flags.append(("drift_hint", drift))

        # compute severity
        severity = compute_severity(flags)

        # recommended actions (simple mapping)
        recommended = []
        for code, _ in flags:
            if code == "missing_artifact":
                recommended.append("Ensure model checkpoints/artifacts are being saved to the configured storage.")
            if code == "high_fail_rate":
                recommended.append("Investigate failing tests and logs; rerun failed cases locally.")
            if code in ("overfit_warning", "overfit_fail"):
                recommended.append("Consider regularization (dropout), reduce model complexity, or get more data.")
            if code == "metric_spike":
                recommended.append("Inspect recent training logs for instability or preemption incidents.")
            if code == "high_variance":
                recommended.append("Run additional runs to confirm variability, consider averaging or smoothing metrics.")
            if code == "drift_hint":
                recommended.append("Compare with historical runs in Memory Bank for drift analysis.")

        # prepare LLM-ready explanation (placeholder text)
        llm_explanation = "Diagnosis summary ready. For full natural language reasoning, call Gemini with the summary+context."

        # final structured output
        out = {
            "run_id": exp.get("run_id"),
            "severity_score": severity,
            "flags": [{"code": c, "message": m} for c, m in flags],
            "recommended_actions": recommended,
            "llm_explanation": llm_explanation,
            "raw_metrics": metrics
        }

        return respond(out)

    except Exception as e:
        return respond({"error": str(e)})
