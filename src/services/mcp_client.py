# src/services/mcp_client.py
import requests
import os
from typing import Dict, Any

MCP_HOST = os.getenv("MCP_HOST", "http://127.0.0.1:9000")

def call_baseline(metrics: Dict[str, Any], run_id: str = None, top_k: int = 5) -> Dict[str, Any]:
    url = f"{MCP_HOST}/baseline_compare"
    payload = {"run_id": run_id, "metrics": metrics, "top_k": top_k}
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()["result"]

def call_anomaly(metrics: Dict[str, Any], run_id: str = None, sensitivity: float = 2.0) -> Dict[str, Any]:
    url = f"{MCP_HOST}/anomaly_detect"
    payload = {"run_id": run_id, "metrics": metrics, "sensitivity": sensitivity}
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()["result"]
