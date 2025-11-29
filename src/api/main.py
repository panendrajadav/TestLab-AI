"""
FastAPI Application for TestLab-AI

Provides REST API endpoint for running the full pipeline:
INGEST → DIAGNOSIS → ML_IMPROVEMENT → EVALUATION → PLANNER

Also serves static frontend build (monorepo setup).
"""

import json
import sys
import os
import time
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from adk_agents.coordinator_agent import coordinator_agent
try:
    from google.genai.types import Content, Part
except ImportError:
    Content = dict
    Part = dict

app = FastAPI(
    title="TestLab-AI Pipeline",
    description="ML experiment analysis pipeline with diagnosis, improvement suggestions, evaluation, and planning",
    version="1.0.0"
)

class ExperimentRequest(BaseModel):
    """Request model for experiment data"""
    run_id: str = None
    model: str = None
    hyperparameters: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}
    timestamp: str = None
    # Support for custom format
    experiment_id: str = None
    results: Dict[str, Any] = {}
    status: str = None
    created_at: str = None
    name: str = None
    description: str = None

class PipelineResponse(BaseModel):
    """Response model for pipeline results"""
    run_id: str
    pipeline_status: str
    timestamps: Dict[str, Any]
    ingest: Dict[str, Any]
    diagnosis: Dict[str, Any]
    ml_improvement: Dict[str, Any]
    evaluation: Dict[str, Any]
    planner: Dict[str, Any]
    summary: Dict[str, Any] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "TestLab-AI Pipeline",
        "status": "running",
        "endpoints": {
            "pipeline": "/api/run_pipeline",
            "health": "/api/health"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "pipeline": "Advanced",
        "stages": [
            "ingest",
            "diagnosis", 
            "ml_improvement",
            "evaluation",
            "planner"
        ]
    }


@app.get("/api/health")
async def api_health_check():
    """Alias for frontend requests that use /api/ prefix"""
    return await health_check()

@app.post("/api/run_pipeline", response_model=Dict[str, Any])
async def run_pipeline(experiment: ExperimentRequest):
    """
    Run the full advanced pipeline on experiment data
    
    Pipeline stages:
    1. INGEST - Normalize experiment data
    2. DIAGNOSIS - Analyze metrics and detect issues (calls MCP tools)
    3. ML_IMPROVEMENT - Generate improvement recommendations
    4. EVALUATION - Evaluate current state
    5. PLANNER - Create action plan
    
    Returns comprehensive report with all stage outputs
    """
    try:
        # Convert Pydantic model to dict
        experiment_data = experiment.dict(exclude_none=True)
        
        # Create Content request for coordinator
        try:
            content_request = Content(parts=[Part(text=json.dumps(experiment_data))])
        except:
            content_request = {"parts": [{"text": json.dumps(experiment_data)}]}
        
        # Call coordinator agent
        response = coordinator_agent(content_request)
        
        # Extract response data
        if hasattr(response, 'candidates') and response.candidates:
            result_text = response.candidates[0].content.parts[0].text
            result_data = json.loads(result_text)
            return result_data
        else:
            raise HTTPException(
                status_code=500,
                detail="Invalid response from coordinator agent"
            )
            
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON in request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(e)}"
        )

@app.post("/api/run_pipeline_simple")
async def run_pipeline_simple(data: Dict[str, Any]):
    """
    Simplified endpoint that accepts raw JSON data
    """
    try:
        # Create Content request for coordinator
        try:
            content_request = Content(parts=[Part(text=json.dumps(data))])
        except:
            content_request = {"parts": [{"text": json.dumps(data)}]}
        
        # Call coordinator agent
        response = coordinator_agent(content_request)
        
        # Extract response data
        if hasattr(response, 'candidates') and response.candidates:
            result_text = response.candidates[0].content.parts[0].text
            result_data = json.loads(result_text)
            return result_data
        else:
            raise HTTPException(
                status_code=500,
                detail="Invalid response from coordinator agent"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(e)}"
        )

@app.post("/api/run_pipeline_realtime")
async def run_pipeline_realtime(data: Dict[str, Any]):
    """
    Run pipeline with Server-Sent Events (SSE) for real-time updates
    """
    async def event_generator():
        try:
            # Create Content request for coordinator
            try:
                content_request = Content(parts=[Part(text=json.dumps(data))])
            except:
                content_request = {"parts": [{"text": json.dumps(data)}]}
            
            # Send start event
            yield f"data: {json.dumps({'step': 'server', 'status': 'processing', 'message': 'Starting pipeline...', 'run_id': data.get('run_id', 'unknown')})}\n\n"
            
            # Call coordinator agent
            response = coordinator_agent(content_request)
            
            # Extract response data
            if hasattr(response, 'candidates') and response.candidates:
                result_text = response.candidates[0].content.parts[0].text
                result_data = json.loads(result_text)
                
                # Send each stage as it completes
                stages = ['ingest', 'diagnosis', 'ml_improvement', 'evaluation', 'planner']
                for stage in stages:
                    stage_data = result_data.get(stage, {})
                    status = 'completed' if stage_data and 'error' not in stage_data else 'error'
                    message = stage_data.get('error', f'{stage} completed') if status == 'error' else f'{stage} completed'
                    
                    yield f"data: {json.dumps({'step': stage, 'status': status, 'message': message, 'run_id': result_data.get('run_id'), 'result': stage_data})}\n\n"
                
                # Send final result
                yield f"data: {json.dumps({'step': 'complete', 'status': 'completed', 'message': 'Pipeline complete', 'final_result': result_data})}\n\n"
            else:
                yield f"data: {json.dumps({'step': 'error', 'status': 'error', 'message': 'Invalid response from coordinator agent'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'step': 'error', 'status': 'error', 'message': f'Pipeline execution failed: {str(e)}'})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ============ MONOREPO SETUP: SERVE STATIC FRONTEND ============
# Serve static files from frontend build output
dist_path = os.path.join(os.path.dirname(__file__), '../../dist/client')
if os.path.isdir(dist_path):
    app.mount("/static", StaticFiles(directory=dist_path), name="static")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """
    Serve React SPA from dist/client
    Falls back to index.html for client-side routing
    """
    # Skip API routes
    if full_path.startswith("api/"):
        return {"error": "API route not found", "path": full_path}
    
    file_path = os.path.join(dist_path, full_path)
    
    # If file exists, serve it
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Otherwise, serve index.html for client-side routing
    index_path = os.path.join(dist_path, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    
    # Fallback if dist not built yet
    return {"message": "Frontend not built. Run 'npm run build' in frontend/ folder."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)