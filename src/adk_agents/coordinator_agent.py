"""
Coordinator Agent (ADK-compliant)

Orchestrates the full Option B pipeline:
Ingest → Diagnosis → ML Improvement → Evaluation → Planner

Calls all agents in sequence and merges responses into a final report.
"""

import json
import time
from datetime import datetime
from typing import Any, Dict

try:
    from google.genai.types import Content, GenerateContentResponse, Part
except ImportError:
    Content = dict
    GenerateContentResponse = dict
    Part = dict

# Import all agents
from adk_agents.ingest_agent import ingest_agent
from adk_agents.diagnosis_agent import diagnosis_agent
from adk_agents.ml_improvement_agent import ml_improvement_agent
from adk_agents.eval_agent import eval_agent
from adk_agents.planner_agent import planner_agent


def respond(obj: Any):
    """Helper to create ADK-compliant response"""
    txt = json.dumps(obj, indent=2)
    try:
        return GenerateContentResponse(candidates=[{"content": Content(parts=[Part(text=txt)])}])
    except:
        return {"candidates": [{"content": {"parts": [{"text": txt}]}}]}


def extract_response_data(response: GenerateContentResponse) -> Dict[str, Any]:
    """Extract JSON data from ADK response"""
    try:
        if hasattr(response, 'candidates') and response.candidates:
            text = response.candidates[0].content.parts[0].text
            return json.loads(text)
        return {"error": "Invalid response format"}
    except Exception as e:
        return {"error": f"Failed to parse response: {str(e)}"}


def create_content_request(data: Dict[str, Any]):
    """Create Content object for agent requests"""
    try:
        return Content(parts=[Part(text=json.dumps(data))])
    except:
        return {"parts": [{"text": json.dumps(data)}]}


def coordinator_agent(request) -> GenerateContentResponse:
    """
    Coordinator Agent - ADK Entry Point
    
    Orchestrates the full pipeline:
    1. Ingest Agent - normalizes input data
    2. Diagnosis Agent - analyzes metrics and flags issues  
    3. ML Improvement Agent - suggests improvements
    4. Evaluation Agent - evaluates current state
    5. Planner Agent - creates action plan
    
    Returns comprehensive report with all agent outputs.
    """
    
    start_time = time.time()
    timestamps = {
        "pipeline_start": datetime.now().isoformat(),
        "stages": {}
    }
    
    try:
        # Handle both Content object and direct dict input
        if hasattr(request, 'parts'):
            raw = request.parts[0].text
            initial_data = json.loads(raw)
        else:
            initial_data = request
            
        run_id = initial_data.get("run_id", f"coord_{int(time.time())}")
        
        # Initialize final report structure
        final_report = {
            "run_id": run_id,
            "timestamps": timestamps,
            "pipeline_status": "running",
            "ingest": {},
            "diagnosis": {},
            "ml_improvement": {},
            "evaluation": {},
            "planner": {}
        }
        
        # STAGE 1: INGEST AGENT
        print(f"[COORDINATOR] Starting Ingest Agent for run_id: {run_id}")
        stage_start = time.time()
        timestamps["stages"]["ingest_start"] = datetime.now().isoformat()
        
        try:
            ingest_request = create_content_request(initial_data)
            ingest_response = ingest_agent(ingest_request)
            ingest_data = extract_response_data(ingest_response)
            final_report["ingest"] = ingest_data
            timestamps["stages"]["ingest_end"] = datetime.now().isoformat()
            timestamps["stages"]["ingest_duration"] = time.time() - stage_start
            print(f"[COORDINATOR] Ingest completed in {timestamps['stages']['ingest_duration']:.2f}s")
        except Exception as e:
            final_report["ingest"] = {"error": f"Ingest failed: {str(e)}"}
            print(f"[COORDINATOR] Ingest failed: {e}")
        
        # STAGE 2: DIAGNOSIS AGENT
        print(f"[COORDINATOR] Starting Diagnosis Agent")
        stage_start = time.time()
        timestamps["stages"]["diagnosis_start"] = datetime.now().isoformat()
        
        try:
            # Use normalized data from ingest, fallback to original
            diagnosis_input = ingest_data.get("normalized", initial_data)
            diagnosis_request = create_content_request(diagnosis_input)
            diagnosis_response = diagnosis_agent(diagnosis_request)
            diagnosis_data = extract_response_data(diagnosis_response)
            final_report["diagnosis"] = diagnosis_data
            timestamps["stages"]["diagnosis_end"] = datetime.now().isoformat()
            timestamps["stages"]["diagnosis_duration"] = time.time() - stage_start
            print(f"[COORDINATOR] Diagnosis completed in {timestamps['stages']['diagnosis_duration']:.2f}s")
        except Exception as e:
            final_report["diagnosis"] = {"error": f"Diagnosis failed: {str(e)}"}
            print(f"[COORDINATOR] Diagnosis failed: {e}")
        
        # STAGE 3: ML IMPROVEMENT AGENT
        print(f"[COORDINATOR] Starting ML Improvement Agent")
        stage_start = time.time()
        timestamps["stages"]["ml_improvement_start"] = datetime.now().isoformat()
        
        try:
            # Pass diagnosis results to ML improvement
            ml_improvement_request = create_content_request(diagnosis_data)
            ml_improvement_response = ml_improvement_agent(ml_improvement_request)
            ml_improvement_data = extract_response_data(ml_improvement_response)
            final_report["ml_improvement"] = ml_improvement_data
            timestamps["stages"]["ml_improvement_end"] = datetime.now().isoformat()
            timestamps["stages"]["ml_improvement_duration"] = time.time() - stage_start
            print(f"[COORDINATOR] ML Improvement completed in {timestamps['stages']['ml_improvement_duration']:.2f}s")
        except Exception as e:
            final_report["ml_improvement"] = {"error": f"ML Improvement failed: {str(e)}"}
            print(f"[COORDINATOR] ML Improvement failed: {e}")
        
        # STAGE 4: EVALUATION AGENT
        print(f"[COORDINATOR] Starting Evaluation Agent")
        stage_start = time.time()
        timestamps["stages"]["evaluation_start"] = datetime.now().isoformat()
        
        try:
            # Combine diagnosis and ML improvement data for evaluation
            eval_input = {
                "run_id": run_id,
                "diagnosis": diagnosis_data,
                "ml_improvement": ml_improvement_data,
                "original_metrics": initial_data.get("metrics", {})
            }
            eval_request = create_content_request(eval_input)
            eval_response = eval_agent(eval_request)
            eval_data = extract_response_data(eval_response)
            final_report["evaluation"] = eval_data
            timestamps["stages"]["evaluation_end"] = datetime.now().isoformat()
            timestamps["stages"]["evaluation_duration"] = time.time() - stage_start
            print(f"[COORDINATOR] Evaluation completed in {timestamps['stages']['evaluation_duration']:.2f}s")
        except Exception as e:
            final_report["evaluation"] = {"error": f"Evaluation failed: {str(e)}"}
            print(f"[COORDINATOR] Evaluation failed: {e}")
        
        # STAGE 5: PLANNER AGENT
        print(f"[COORDINATOR] Starting Planner Agent")
        stage_start = time.time()
        timestamps["stages"]["planner_start"] = datetime.now().isoformat()
        
        try:
            # Combine all previous results for planning
            planner_input = {
                "run_id": run_id,
                "ingest": ingest_data,
                "diagnosis": diagnosis_data,
                "ml_improvement": ml_improvement_data,
                "evaluation": eval_data
            }
            planner_request = create_content_request(planner_input)
            planner_response = planner_agent(planner_request)
            planner_data = extract_response_data(planner_response)
            final_report["planner"] = planner_data
            timestamps["stages"]["planner_end"] = datetime.now().isoformat()
            timestamps["stages"]["planner_duration"] = time.time() - stage_start
            print(f"[COORDINATOR] Planner completed in {timestamps['stages']['planner_duration']:.2f}s")
        except Exception as e:
            final_report["planner"] = {"error": f"Planner failed: {str(e)}"}
            print(f"[COORDINATOR] Planner failed: {e}")
        
        # Finalize report
        total_duration = time.time() - start_time
        timestamps["pipeline_end"] = datetime.now().isoformat()
        timestamps["total_duration"] = total_duration
        final_report["pipeline_status"] = "completed"
        
        # Add summary
        final_report["summary"] = {
            "total_duration_seconds": total_duration,
            "stages_completed": len([k for k in final_report.keys() if k not in ["run_id", "timestamps", "pipeline_status", "summary"] and "error" not in final_report[k]]),
            "stages_failed": len([k for k in final_report.keys() if k not in ["run_id", "timestamps", "pipeline_status", "summary"] and "error" in final_report[k]]),
            "overall_severity": diagnosis_data.get("severity_label", "UNKNOWN"),
            "key_recommendations": ml_improvement_data.get("recommendations", [])[:3]
        }
        
        print(f"[COORDINATOR] Pipeline completed in {total_duration:.2f}s")
        return respond(final_report)
        
    except Exception as e:
        # Pipeline-level error
        timestamps["pipeline_end"] = datetime.now().isoformat()
        timestamps["total_duration"] = time.time() - start_time
        
        error_report = {
            "run_id": initial_data.get("run_id", "unknown"),
            "timestamps": timestamps,
            "pipeline_status": "failed",
            "error": str(e),
            "partial_results": final_report if 'final_report' in locals() else {}
        }
        
        print(f"[COORDINATOR] Pipeline failed: {e}")
        return respond(error_report)