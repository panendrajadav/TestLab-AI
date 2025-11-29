# src/mcp_tools/mcp_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tools.baseline_comparator import baseline_compare_handler
from mcp_tools.anomaly_detector import anomaly_detect_handler

app = FastAPI(title="TestLab-AI MCP Tools", version="0.1")

class BaselineRequest(BaseModel):
    run_id: Optional[str] = None
    metrics: Dict[str, Any]
    top_k: int = 5  # how many past runs to use for baseline

class AnomalyRequest(BaseModel):
    run_id: Optional[str] = None
    metrics: Dict[str, Any]
    sensitivity: float = 2.0  # z-score threshold

@app.post("/baseline_compare")
def baseline_compare(req: BaselineRequest):
    try:
        res = baseline_compare_handler(req.metrics, req.run_id, top_k=req.top_k)
        return {"status": "ok", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/anomaly_detect")
def anomaly_detect(req: AnomalyRequest):
    try:
        res = anomaly_detect_handler(req.metrics, req.run_id, sensitivity=req.sensitivity)
        return {"status": "ok", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("mcp_server:app", host="127.0.0.1", port=9000, reload=True)
