"""
Ultra-rich Diagnosis Agent (ADK-compliant)

Features:
- Integrates with local MCP tools (baseline_compare, anomaly_detect) via services.mcp_client
- Internal checks: overfit, underfit, instability, test fail rates, missing artifacts
- Merges MCP results into flags and recommendations
- Computes weighted severity score and label (LOW/MEDIUM/HIGH)
- Returns ADK-compliant GenerateContentResponse with structured JSON
- Provides an LLM-ready explanation payload (placeholder) for Planner
"""

import json
import math
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google.genai.types import Content, GenerateContentResponse

# MCP client helper (uses requests to call the local MCP server)
from services.mcp_client import call_anomaly, call_baseline

load_dotenv()

# Thresholds and weights (tunable)
TH = {
    "overfit_pct": 0.10,
    "loss_high_abs": 1.0,
    "unstable_relstd": 0.10,
    "fail_rate_warning": 0.10,
    "fail_rate_high": 0.25,
    "regression_pct": 0.05
}

WEIGHTS = {
    "critical": 0.5,
    "high": 0.35,
    "medium": 0.15,
    "mcp_anomaly": 0.3,
    "mcp_regression": 0.4
}


# ---------- ADK response helper ----------
def respond(obj: Any) -> GenerateContentResponse:
    txt = json.dumps(obj, indent=2)
    return GenerateContentResponse(candidates=[{"content": Content(parts=[{"text": txt}])}])


# ---------- utility helpers ----------
def safe_get(metrics: Dict[str, Any], names: List[str]):
    for n in names:
        if n in metrics:
            return metrics[n]
    return None


def compute_rel_std(values: List[float]) -> Optional[float]:
    if not values or len(values) < 2:
        return None
    n = len(values)
    mean_val = sum(values) / n
    if mean_val == 0:
        return None
    var = sum((x - mean_val) ** 2 for x in values) / (n - 1)
    std = math.sqrt(var)
    return std / mean_val


def ensure_list(v):
    if isinstance(v, list):
        return v
    return None


def add_flag(flags: List[Dict[str, Any]], code: str, level: str, message: str, meta: Optional[Dict] = None):
    flags.append({
        "code": code,
        "level": level,  # CRITICAL / HIGH / MEDIUM / INFO
        "message": message,
        "meta": meta or {}
    })


# ---------- internal checks ----------
def check_overfit(metrics: Dict[str, Any]) -> Optional[Dict]:
    train_loss = safe_get(metrics, ["train_loss", "train_loss_value"])
    val_loss = safe_get(metrics, ["val_loss", "validation_loss", "val_loss_value"])
    if train_loss is None or val_loss is None:
        return None
    try:
        if train_loss > 0:
            pct = (val_loss - train_loss) / max(train_loss, 1e-9)
            if pct > TH["overfit_pct"]:
                return {"code": "overfit", "pct": pct, "train_loss": train_loss, "val_loss": val_loss}
    except Exception:
        pass
    return None


def check_underfit(metrics: Dict[str, Any]) -> Optional[Dict]:
    train_loss = safe_get(metrics, ["train_loss", "train_loss_value"])
    val_loss = safe_get(metrics, ["val_loss", "validation_loss"])
    acc = safe_get(metrics, ["accuracy", "acc", "val_accuracy"])
    if train_loss is None or val_loss is None:
        return None
    if train_loss > TH["loss_high_abs"] and val_loss > TH["loss_high_abs"]:
        if acc is None or acc < 0.6:
            return {"code": "underfit", "train_loss": train_loss, "val_loss": val_loss, "accuracy": acc}
    return None


def check_instability(metrics: Dict[str, Any]) -> List[Dict]:
    issues = []
    for k, v in metrics.items():
        arr = ensure_list(v)
        if arr:
            relstd = compute_rel_std(arr)
            if relstd is not None and relstd > TH["unstable_relstd"]:
                issues.append({"code": "unstable_metric", "metric": k, "rel_std": relstd})
    return issues


def check_test_failures(metrics: Dict[str, Any]) -> Optional[Dict]:
    if "failed" in metrics and "total_tests" in metrics:
        try:
            failed = metrics.get("failed", 0)
            total = metrics.get("total_tests", 0)
            if total > 0:
                fail_rate = failed / total
                if fail_rate >= TH["fail_rate_high"]:
                    return {"code": "high_fail_rate", "fail_rate": fail_rate}
                if fail_rate >= TH["fail_rate_warning"]:
                    return {"code": "moderate_fail_rate", "fail_rate": fail_rate}
        except Exception:
            pass
    return None


def artifact_check(exp: Dict[str, Any]) -> Optional[Dict]:
    # Check for presence of typical artifact fields (checkpoint / artifacts)
    artifacts = exp.get("artifacts") or exp.get("checkpoint") or exp.get("checkpoints")
    if not artifacts:
        return {"code": "missing_artifact", "message": "No artifacts (checkpoint) found."}
    return None


# ---------- combine results and score ----------
def compute_weighted_score(flags: List[Dict[str, Any]], mcp_results: Dict[str, Any]) -> float:
    score = 0.0
    # map levels
    for f in flags:
        lvl = f.get("level", "INFO").upper()
        if lvl == "CRITICAL":
            score += WEIGHTS["critical"]
        elif lvl == "HIGH":
            score += WEIGHTS["high"]
        elif lvl == "MEDIUM":
            score += WEIGHTS["medium"]
        else:
            score += 0.0

    # MCP anomalies
    if mcp_results and isinstance(mcp_results, dict):
        anomaly_score = mcp_results.get("summary_score", 0.0)
        score += anomaly_score * WEIGHTS["mcp_anomaly"]
        # regression presence increases score
        comp = mcp_results.get("comparison") or {}
        for k, v in comp.items():
            z = v.get("z")
            if z is not None and abs(z) > 2.5:
                score += WEIGHTS["mcp_regression"]

    # clamp 0..1
    return max(0.0, min(1.0, score))


def severity_label_from_score(score: float) -> str:
    if score >= 0.6:
        return "HIGH"
    if score >= 0.25:
        return "MEDIUM"
    return "LOW"


def assemble_recommendations(flags: List[Dict[str, Any]], mcp_results: Dict[str, Any]) -> List[str]:
    recs = []
    # generate based on flags
    for f in flags:
        code = f.get("code", "")
        if "overfit" in code:
            recs.append("Reduce overfitting: add regularization (dropout), use early stopping, or augment data.")
        elif "underfit" in code:
            recs.append("Address underfitting: increase model capacity, train longer, or tune optimizer/hyperparams.")
        elif "unstable_metric" in code:
            recs.append("Stabilize training: reduce LR, increase batch size, or add gradient clipping and check pipeline.")
        elif "fail_rate" in code:
            recs.append("Inspect failing tests; cluster failures and create focused test cases; prioritize fixes.")
        elif "missing_artifact" in code:
            recs.append("Ensure model checkpoints/artifacts are saved to configured storage and accessible.")
        elif "regression" in code:
            recs.append("Compare checkpoints and hyperparameters vs baseline; consider rollback or A/B tests.")

    # incorporate MCP suggestions
    if mcp_results:
        comp = mcp_results.get("comparison", {})
        for metric, info in comp.items():
            z = info.get("z")
            if z is not None and abs(z) > 2.5:
                recs.append(f"Metric '{metric}' deviates from baseline (z={z:.2f}). Investigate data/labels.")
    if not recs:
        recs.append("No immediate actions detected; monitor and collect more runs for stable baselines.")
    # deduplicate
    dedup = []
    for r in recs:
        if r not in dedup:
            dedup.append(r)
    return dedup


# ---------- ADK Entrypoint ----------
def diagnosis_agent(request: Content) -> GenerateContentResponse:
    """
    Input contract:
      Accepts either:
        - normalized experiment dict in request.parts[0].text
        - or wrapper: {"normalized": {...}, "baseline": {...}}
    Returns:
      ADK-compliant GenerateContentResponse with fields:
        run_id, severity_score (0..100), severity_label, flags (grouped), recommended_actions,
        mcp_results (baseline + anomaly), llm_payload (placeholder), raw_metrics
    """
    try:
        raw = request.parts[0].text
        data = json.loads(raw)
        exp = data.get("normalized", data)
        run_id = exp.get("run_id", exp.get("experiment_id", "unknown"))
        metrics = exp.get("metrics", {}) or {}

        flags: List[Dict[str, Any]] = []

        # Internal deterministic checks
        of = check_overfit(metrics)
        if of:
            add_flag(flags, "overfit", "HIGH", f"Validation loss higher than training loss by {of['pct']:.1%}", of)

        uf = check_underfit(metrics)
        if uf:
            add_flag(flags, "underfit", "HIGH", "High train & val loss with low accuracy", uf)

        instability = check_instability(metrics)
        for inst in instability:
            add_flag(flags, "unstable_metric", "MEDIUM", f"Metric {inst['metric']} shows high relative std {inst['rel_std']:.2f}", inst)

        tf = check_test_failures(metrics)
        if tf:
            level = "HIGH" if tf["code"] == "high_fail_rate" else "MEDIUM"
            add_flag(flags, tf["code"], level, f"Fail rate: {tf.get('fail_rate')}", tf)

        art = artifact_check(exp)
        if art:
            add_flag(flags, art.get("code", "missing_artifact"), "MEDIUM", art.get("message", ""), art)

        # Call MCP tools (best-effort)
        mcp_baseline = None
        mcp_anomaly = None
        try:
            mcp_baseline = call_baseline(metrics, run_id=run_id, top_k=5)
        except Exception as e:
            add_flag(flags, "mcp_baseline_error", "INFO", f"Baseline tool error: {str(e)}", {"error": str(e)})

        try:
            mcp_anomaly = call_anomaly(metrics, run_id=run_id, sensitivity=2.0)
        except Exception as e:
            add_flag(flags, "mcp_anomaly_error", "INFO", f"Anomaly tool error: {str(e)}", {"error": str(e)})

        # incorporate MCP anomaly findings
        if mcp_anomaly and isinstance(mcp_anomaly, dict):
            anomalies = mcp_anomaly.get("anomalies", [])
            for a in anomalies:
                sev = "HIGH" if a.get("severity") == "HIGH" else ("MEDIUM" if a.get("severity") == "MEDIUM" else "INFO")
                add_flag(flags, f"mcp_{a.get('type', 'anomaly')}", sev, f"Anomaly detected: {a.get('metric')} ({a.get('type')})", a)

        # incorporate MCP baseline regressions (z-score based)
        if mcp_baseline and isinstance(mcp_baseline, dict):
            comp = mcp_baseline.get("comparison", {})
            for metric, info in comp.items():
                z = info.get("z")
                if z is not None:
                    if abs(z) > 3.0:
                        add_flag(flags, f"regression_{metric}", "HIGH", f"Large deviation vs baseline (z={z:.2f})", {"metric": metric, "z": z})
                    elif abs(z) > 2.5:
                        add_flag(flags, f"regression_{metric}", "MEDIUM", f"Moderate deviation vs baseline (z={z:.2f})", {"metric": metric, "z": z})

        # compute weighted severity score 0..1 then scale to 0..100
        weighted = compute_weighted_score(flags, mcp_baseline or {})
        severity_label = severity_label_from_score(weighted)
        severity_score_pct = round(weighted * 100, 2)

        # assemble recommendations
        recommendations = assemble_recommendations(flags, mcp_baseline or {})

        # prepare LLM-ready explanation payload (compact)
        llm_payload = {
            "run_id": run_id,
            "summary": {
                "severity_score_pct": severity_score_pct,
                "severity_label": severity_label,
                "top_flags": flags[:5]
            },
            "context": {
                "metrics": metrics,
                "mcp_baseline": mcp_baseline,
                "mcp_anomaly": mcp_anomaly
            },
            "instructions": "Produce a concise diagnostic summary and prioritized remediation plan (max 300 words)."
        }

        # final structured output
        out = {
            "run_id": run_id,
            "severity_label": severity_label,
            "severity_score_pct": severity_score_pct,
            "flags": flags,
            "recommended_actions": recommendations,
            "mcp_results": {
                "baseline": mcp_baseline,
                "anomaly": mcp_anomaly
            },
            "llm_payload": llm_payload,
            "raw_metrics": metrics
        }

        return respond(out)

    except Exception as e:
        return respond({"error": str(e)})
