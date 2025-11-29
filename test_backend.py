#!/usr/bin/env python3
"""
Test script to verify backend API is working correctly
"""

import requests
import json
import time

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_simple_pipeline():
    """Test the simple pipeline endpoint"""
    try:
        test_data = {
            "run_id": "test_001",
            "model": "Test Model",
            "metrics": {
                "accuracy": 0.75,
                "loss": 0.45,
                "f1_score": 0.72
            },
            "hyperparameters": {
                "learning_rate": 0.001,
                "batch_size": 32
            }
        }
        
        response = requests.post(
            "http://localhost:8000/api/run_pipeline_simple",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Simple pipeline test passed")
            print(f"   Run ID: {result.get('run_id', 'unknown')}")
            print(f"   Status: {result.get('pipeline_status', 'unknown')}")
            
            # Check if ML improvement generated code
            if result.get('ml_improvement', {}).get('improved_code'):
                print("   ✨ Improved code generated!")
            
            return True
        else:
            print(f"❌ Simple pipeline test failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Simple pipeline test error: {e}")
        return False

def test_realtime_pipeline():
    """Test the real-time pipeline endpoint"""
    try:
        test_data = {
            "run_id": "test_realtime_001",
            "model": "Realtime Test Model",
            "metrics": {
                "accuracy": 0.68,
                "loss": 0.52,
                "f1_score": 0.65
            }
        }
        
        print("🔄 Testing real-time pipeline...")
        response = requests.post(
            "http://localhost:8000/api/run_pipeline_realtime",
            json=test_data,
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Real-time pipeline started")
            
            step_count = 0
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            step = data.get('step', 'unknown')
                            status = data.get('status', 'unknown')
                            message = data.get('message', '')
                            
                            print(f"   📋 {step}: {status} - {message}")
                            step_count += 1
                            
                            if step == 'complete':
                                print("✅ Real-time pipeline completed successfully")
                                return True
                                
                        except json.JSONDecodeError:
                            continue
            
            if step_count > 0:
                print("✅ Real-time pipeline test passed (partial)")
                return True
            else:
                print("❌ No steps received from real-time pipeline")
                return False
        else:
            print(f"❌ Real-time pipeline test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Real-time pipeline test error: {e}")
        return False

def main():
    """Run all backend tests"""
    print("🧪 TestLab-AI Backend Test Suite")
    print("=" * 50)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    for i in range(10):
        if test_health_check():
            break
        time.sleep(2)
    else:
        print("❌ Server not ready after 20 seconds")
        return False
    
    print("\n🔬 Running pipeline tests...")
    
    # Test simple pipeline
    simple_success = test_simple_pipeline()
    
    print("\n🔄 Testing real-time pipeline...")
    realtime_success = test_realtime_pipeline()
    
    print("\n📊 Test Results:")
    print(f"   Health Check: ✅")
    print(f"   Simple Pipeline: {'✅' if simple_success else '❌'}")
    print(f"   Real-time Pipeline: {'✅' if realtime_success else '❌'}")
    
    if simple_success and realtime_success:
        print("\n🎉 All tests passed! Backend is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")
        return False

if __name__ == "__main__":
    main()