#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script to validate SSE pipeline events
"""

import requests
import json
import time

def test_sse_pipeline():
    """Test the event-driven pipeline SSE endpoint"""
    
    # Sample experiment data
    test_data = {
        "run_id": f"test_{int(time.time())}",
        "model": "Test ML Model",
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
    
    print("[TEST] Testing Event-Driven Pipeline SSE")
    print(f"[DATA] Test Data: {json.dumps(test_data, indent=2)}")
    print("\n[SSE] Starting SSE stream...\n")
    
    try:
        # Make request to SSE endpoint
        response = requests.post(
            "http://localhost:8000/api/run_pipeline_realtime",
            json=test_data,
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Request failed: {response.status_code} - {response.text}")
            return
        
        # Process SSE events
        event_count = 0
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                try:
                    event_data = json.loads(line[6:])  # Remove 'data: ' prefix
                    event_count += 1
                    
                    agent = event_data.get('agent', 'unknown')
                    status = event_data.get('status', 'unknown')
                    timestamp = event_data.get('timestamp', '')
                    
                    # Format timestamp
                    if timestamp:
                        time_str = timestamp.split('T')[1][:8]  # Extract HH:MM:SS
                    else:
                        time_str = "??:??:??"
                    
                    # Status icons
                    icon = {
                        'started': '[START]',
                        'processing': '[PROC]',
                        'success': '[OK]',
                        'failed': '[FAIL]'
                    }.get(status, '[?]')
                    
                    print(f"[{time_str}] {icon} {agent}: {status}")
                    
                    # Show payload info for key events
                    if event_data.get('payload'):
                        payload = event_data['payload']
                        if agent == 'ml_improvement_agent' and 'improved_code' in payload:
                            print(f"    [CODE] Generated improved code ({len(payload['improved_code'])} chars)")
                        elif agent == 'pipeline' and status == 'success':
                            print(f"    [DONE] Pipeline completed successfully!")
                            print(f"    [RESULT] Final result keys: {list(payload.keys())}")
                            break
                    
                    # Handle errors
                    if status == 'failed':
                        error = event_data.get('error', 'Unknown error')
                        print(f"    [ERROR] Error: {error}")
                        break
                        
                except json.JSONDecodeError as e:
                    print(f"[WARN] Failed to parse event: {line}")
                    continue
        
        print(f"\n[SUCCESS] Test completed! Processed {event_count} events.")
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection failed. Make sure the backend server is running on localhost:8000")
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

def test_health_check():
    """Test if the backend is running"""
    try:
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            print("[OK] Backend health check passed")
            return True
        else:
            print(f"[WARN] Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Backend is not running on localhost:8000")
        return False

if __name__ == "__main__":
    print("TestLab-AI Event-Driven Pipeline Test\n")
    
    # Check if backend is running
    if test_health_check():
        print()
        test_sse_pipeline()
    else:
        print("\n[INFO] To start the backend:")
        print("   cd backend && python -m uvicorn api.main:app --reload --port 8000")