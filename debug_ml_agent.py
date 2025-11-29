#!/usr/bin/env python3
"""
Debug script to test ML Improvement Agent directly
"""

import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from adk_agents.ml_improvement_agent import ml_improvement_agent

def test_ml_agent():
    """Test ML Improvement Agent directly"""
    
    # Sample diagnosis data (similar to what diagnosis agent would return)
    test_diagnosis_data = {
        "run_id": "debug_test",
        "raw_metrics": {
            "accuracy": 0.75,
            "loss": 0.45,
            "f1_score": 0.72
        },
        "flags": [
            {
                "code": "missing_artifact",
                "level": "MEDIUM", 
                "message": "No artifacts (checkpoint) found."
            }
        ],
        "mcp_results": {
            "baseline": {
                "baseline": {},
                "comparison": {
                    "accuracy": {"current": 0.75, "delta": None, "z": None}
                }
            },
            "anomaly": {
                "anomalies": [],
                "summary_score": 0.0
            }
        },
        "severity_score_pct": 15.0,
        "severity_label": "LOW"
    }
    
    print("[DEBUG] Testing ML Improvement Agent directly")
    print(f"[INPUT] Test data: {json.dumps(test_diagnosis_data, indent=2)}")
    
    try:
        # Create request object
        request = {"parts": [{"text": json.dumps(test_diagnosis_data)}]}
        
        # Call ML improvement agent
        response = ml_improvement_agent(request)
        
        # Extract response
        if hasattr(response, 'candidates') and response.candidates:
            result_text = response.candidates[0].content.parts[0].text
            result_data = json.loads(result_text)
        else:
            result_text = response["candidates"][0]["content"]["parts"][0]["text"]
            result_data = json.loads(result_text)
        
        print(f"\n[OUTPUT] ML Agent response keys: {list(result_data.keys())}")
        
        if 'error' in result_data:
            print(f"[ERROR] ML Agent returned error: {result_data['error']}")
        else:
            print(f"[SUCCESS] ML Agent completed successfully")
            
            if result_data.get('improved_code'):
                print(f"[CODE] Improved code length: {len(result_data['improved_code'])} chars")
                print(f"[CODE] First 300 chars: {result_data['improved_code'][:300]}...")
            else:
                print(f"[WARNING] No improved_code in response")
            
            if result_data.get('recommendations'):
                print(f"[RECS] Recommendations count: {len(result_data['recommendations'])}")
                for i, rec in enumerate(result_data['recommendations'][:3]):
                    print(f"[RECS] {i+1}. {rec}")
        
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ml_agent()