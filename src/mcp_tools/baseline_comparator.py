# src/mcp_tools/baseline_comparator.py
import sqlite3
import json
from typing import Dict, Any, Optional, Tuple
import os
from statistics import mean, pstdev

DB_PATH = os.getenv("DATABASE_PATH", "memory/testlab.db")

def _fetch_all_runs(db_path: str):
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT report_json FROM pipeline_runs ORDER BY ts_created DESC")
    rows = cur.fetchall()
    conn.close()
    runs = []
    for (rjson,) in rows:
        try:
            runs.append(json.loads(rjson))
        except Exception:
            continue
    return runs

def baseline_compare_handler(metrics: Dict[str, Any], run_id: Optional[str] = None, top_k: int = 5):
    """
    Compute baseline statistics for numeric metrics using the last `top_k` pipeline runs.
    Returns:
      {
        "baseline": {metric: {"mean":..., "std":..., "count": n}},
        "comparison": {metric: {"current": v, "delta": v-mean, "z": zscore}}
      }
    """
    runs = _fetch_all_runs(DB_PATH)
    numeric_metrics = {}
    # Extract metric values from previous runs
    history = {}
    count = 0
    for r in runs:
        # Each run stored as pipeline report; try to extract normalized metrics
        norm = None
        try:
            norm = r.get("ingest", {}).get("normalized") or r.get("ingest", {}).get("normalized", r.get("ingest", {}).get("raw"))
            # if nested as object, try deeper
            if isinstance(norm, dict) and "normalized" in norm:
                norm = norm["normalized"]
        except Exception:
            norm = None

        if not norm:
            continue
        m = norm.get("metrics", {})
        if not isinstance(m, dict):
            continue
        # record numeric scalars
        for k, v in m.items():
            if isinstance(v, (int, float)):
                history.setdefault(k, []).append(v)
        count += 1
        if count >= top_k:
            break

    # Compute baseline stats
    baseline = {}
    for k, vals in history.items():
        try:
            baseline[k] = {
                "mean": mean(vals),
                "std": pstdev(vals) if len(vals) > 1 else 0.0,
                "count": len(vals)
            }
        except Exception:
            baseline[k] = {"mean": None, "std": None, "count": len(vals)}

    # Compare current metrics to baseline
    comparison = {}
    for k, cur_v in metrics.items():
        if not isinstance(cur_v, (int, float)):
            continue
        b = baseline.get(k)
        if not b or b["count"] == 0 or b["mean"] is None:
            comparison[k] = {"current": cur_v, "delta": None, "z": None}
        else:
            delta = cur_v - b["mean"]
            z = None
            try:
                z = (cur_v - b["mean"]) / (b["std"] if b["std"] > 0 else 1e-9)
            except Exception:
                z = None
            comparison[k] = {"current": cur_v, "delta": delta, "z": z, "baseline_count": b["count"], "baseline_mean": b["mean"], "baseline_std": b["std"]}

    return {"baseline": baseline, "comparison": comparison}
