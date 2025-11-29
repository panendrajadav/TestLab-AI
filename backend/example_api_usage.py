#!/usr/bin/env python3
"""
Example API usage for TestLab-AI Advanced Pipeline
"""
import requests
import json
import time

# API endpoint
API_BASE = "http://127.0.0.1:8000"

def test_api_health():
    """Test API health check"""
    print("=== Testing API Health ===")
    try:
        response = requests.get(f"{API_BASE}/health")
        response.raise_for_status()
        print(f"Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_ml_experiment_api():
    """Test ML experiment via API"""
    print("\n=== Testing ML Experiment via API ===")
    
    ml_data = {
        "run_id": "api_test_ml_001",
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
    
    try:
        print(f"Sending request to {API_BASE}/run_pipeline")
        print(f"Data: {json.dumps(ml_data, indent=2)}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/run_pipeline",
            json=ml_data,
            timeout=60
        )
        duration = time.time() - start_time
        
        response.raise_for_status()
        result = response.json()
        
        print(f"\n=== API Response (took {duration:.2f}s) ===")
        print(f"Run ID: {result.get('run_id')}")
        print(f"Pipeline Status: {result.get('pipeline_status')}")
        
        # Show stage results
        stages = ['ingest', 'diagnosis', 'ml_improvement', 'evaluation', 'planner']
        for stage in stages:
            stage_data = result.get(stage, {})
            if 'error' in stage_data:
                print(f"{stage.upper()}: ❌ ERROR - {stage_data['error']}")
            else:
                print(f"{stage.upper()}: ✅ SUCCESS")
        
        # Show key insights
        diagnosis = result.get('diagnosis', {})
        if diagnosis and 'severity_label' in diagnosis:
            print(f"\nDiagnosis Severity: {diagnosis['severity_label']}")
            print(f"Severity Score: {diagnosis.get('severity_score_pct', 0)}%")
        
        ml_improvement = result.get('ml_improvement', {})
        if ml_improvement and 'recommendations' in ml_improvement:
            recommendations = ml_improvement['recommendations'][:3]
            print(f"\nTop Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        return result
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_custom_experiment_api():
    """Test custom experiment format via API"""
    print("\n=== Testing Custom Experiment via API ===")
    
    custom_data = {
        "experiment_id": "api_test_custom_001",
        "name": "API Test Custom Experiment",
        "description": "Testing custom format via API",
        "status": "completed",
        "results": {
            "passed": 75,
            "failed": 25,
            "total_tests": 100,
            "success_rate": 0.75
        },
        "created_at": "2024-01-15T11:00:00Z"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/run_pipeline_simple",
            json=custom_data,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Custom experiment processed successfully")
        print(f"Run ID: {result.get('run_id')}")
        print(f"Pipeline Status: {result.get('pipeline_status')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Custom experiment test failed: {e}")
        return None

if __name__ == "__main__":
    print("TestLab-AI Advanced Pipeline - API Usage Example")
    print("=" * 60)
    
    # Check if API is running
    if not test_api_health():
        print("\n❌ API is not running. Please start the API server first:")
        print("   python start_api_server.py")
        exit(1)
    
    # Test ML experiment
    ml_result = test_ml_experiment_api()
    
    # Test custom experiment
    custom_result = test_custom_experiment_api()
    
    print("\n" + "=" * 60)
    if ml_result and custom_result:
        print("✅ All API tests completed successfully!")
    else:
        print("❌ Some API tests failed. Check the output above.")
    
    print("\nTo start the API server:")
    print("  python start_api_server.py")
    print("\nTo start the MCP server (for full functionality):")
    print("  python start_server.py")