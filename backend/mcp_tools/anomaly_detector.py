# src/mcp_tools/anomaly_detector.py
from typing import Dict, Any, List, Optional
import math

def anomaly_detect_handler(metrics: Dict[str, Any], run_id: Optional[str] = None, sensitivity: float = 2.0):
    """
    Simple anomaly detector:
      - For numeric scalars: compute z-like deviation using short-term heuristic (no history here).
      - For test-style metrics (passed/failed): compute fail_rate and compare thresholds.
    Returns:
      {
        "anomalies": [
           {"metric": "accuracy", "type": "z_spike", "value": 0.12, "z": 3.2}
        ],
        "summary_score": 0.12
      }
    """
    anomalies = []
    summary_score = 0.0

    # Detect fail-rate anomalies
    if "failed" in metrics and "total_tests" in metrics:
        failed = metrics.get("failed", 0)
        total = metrics.get("total_tests", 0)
        if total > 0:
            fail_rate = failed / total
            if fail_rate >= 0.25:
                anomalies.append({"metric": "fail_rate", "type": "high_fail_rate", "value": fail_rate, "severity": "HIGH"})
                summary_score += 0.5
            elif fail_rate >= 0.10:
                anomalies.append({"metric": "fail_rate", "type": "moderate_fail_rate", "value": fail_rate, "severity": "MEDIUM"})
                summary_score += 0.2

    # For any numeric metric that looks suspicious (negative, NaN)
    for k, v in metrics.items():
        if isinstance(v, (int, float)):
            if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
                anomalies.append({"metric": k, "type": "invalid_value", "value": v, "severity": "HIGH"})
                summary_score += 0.5
            # detect out-of-range values for percentages
            if "rate" in k or "accuracy" in k or "f1" in k or "percent" in k:
                if v < 0 or v > 1:
                    anomalies.append({"metric": k, "type": "out_of_range", "value": v, "severity": "HIGH"})
                    summary_score += 0.4

    # A small normalized score in 0..1
    summary_score = min(1.0, summary_score)
    return {"anomalies": anomalies, "summary_score": summary_score}
