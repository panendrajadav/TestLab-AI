#!/usr/bin/env python3
"""
Test script for advanced pipeline implementation
"""
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from adk_agents.coordinator_agent import coordinator_agent
from google.genai.types import Content, Part

def test_ml_experiment():
    """Test with ML experiment data"""
    ml_data = {
        "run_id": "test_ml_001",
        "model": "ResNet50",
        "hyperparameters": {
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100
        },
        "metrics": {
            "accuracy": 0.85,
            "train_loss": 0.2,
            "val_loss": 0.35,
            "success_rate": 0.88
        },
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    print("=== Testing ML Experiment ===")
    print(f"Input: {json.dumps(ml_data, indent=2)}")
    
    # Create Content request
    content_request = Content(parts=[Part(text=json.dumps(ml_data))])
    
    # Run pipeline
    response = coordinator_agent(content_request)
    
    # Extract and display results
    if hasattr(response, 'candidates') and response.candidates:
        result_text = response.candidates[0].content.parts[0].text
        result_data = json.loads(result_text)
        
        print("\n=== Pipeline Results ===")
        print(f"Run ID: {result_data.get('run_id')}")
        print(f"Status: {result_data.get('pipeline_status')}")
        print(f"Total Duration: {result_data.get('timestamps', {}).get('total_duration', 'N/A')}s")
        
        # Show key results from each stage
        stages = ['ingest', 'diagnosis', 'ml_improvement', 'evaluation', 'planner']
        for stage in stages:
            stage_data = result_data.get(stage, {})
            if 'error' in stage_data:
                print(f"{stage.upper()}: ERROR - {stage_data['error']}")
            else:
                print(f"{stage.upper()}: SUCCESS")
        
        # Show summary
        summary = result_data.get('summary', {})
        if summary:
            print(f"\nSummary:")
            print(f"  Stages completed: {summary.get('stages_completed', 0)}")
            print(f"  Stages failed: {summary.get('stages_failed', 0)}")
            print(f"  Overall severity: {summary.get('overall_severity', 'UNKNOWN')}")
            
            recommendations = summary.get('key_recommendations', [])
            if recommendations:
                print(f"  Key recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"    {i}. {rec}")
        
        return result_data
    else:
        print("ERROR: Invalid response from coordinator")
        return None

def test_custom_experiment():
    """Test with custom experiment format"""
    custom_data = {
        "experiment_id": "test_custom_001",
        "name": "Custom Test Experiment",
        "description": "Testing custom format",
        "status": "completed",
        "results": {
            "passed": 85,
            "failed": 15,
            "total_tests": 100,
            "success_rate": 0.85
        },
        "created_at": "2024-01-15T11:00:00Z"
    }
    
    print("\n\n=== Testing Custom Experiment ===")
    print(f"Input: {json.dumps(custom_data, indent=2)}")
    
    # Create Content request
    content_request = Content(parts=[Part(text=json.dumps(custom_data))])
    
    # Run pipeline
    response = coordinator_agent(content_request)
    
    # Extract and display results
    if hasattr(response, 'candidates') and response.candidates:
        result_text = response.candidates[0].content.parts[0].text
        result_data = json.loads(result_text)
        
        print("\n=== Pipeline Results ===")
        print(f"Run ID: {result_data.get('run_id')}")
        print(f"Status: {result_data.get('pipeline_status')}")
        
        return result_data
    else:
        print("ERROR: Invalid response from coordinator")
        return None

if __name__ == "__main__":
    print("Testing TestLab-AI Advanced Pipeline Implementation")
    print("=" * 60)
    
    try:
        # Test ML experiment
        ml_result = test_ml_experiment()
        
        # Test custom experiment
        custom_result = test_custom_experiment()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()