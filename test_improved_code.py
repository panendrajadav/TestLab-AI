#!/usr/bin/env python3
"""
Test script to specifically check improved code generation
"""

import requests
import json
import time

def test_improved_code():
    """Test that improved code is properly generated and structured"""
    
    test_data = {
        "run_id": f"improved_code_test_{int(time.time())}",
        "model": "Test ML Model",
        "metrics": {
            "accuracy": 0.75,
            "loss": 0.45,
            "f1_score": 0.72
        }
    }
    
    print("[TEST] Testing Improved Code Generation")
    print(f"[DATA] Test Data: {json.dumps(test_data, indent=2)}")
    print("\n[SSE] Processing events...\n")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/run_pipeline_realtime",
            json=test_data,
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Request failed: {response.status_code}")
            return
        
        ml_improvement_payload = None
        final_result = None
        
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                try:
                    event_data = json.loads(line[6:])
                    
                    # Capture ML improvement agent payload
                    if (event_data.get('agent') == 'ml_improvement_agent' and 
                        event_data.get('status') == 'success'):
                        ml_improvement_payload = event_data.get('payload', {})
                        print(f"[ML_AGENT] ML Improvement Agent completed")
                        if ml_improvement_payload.get('improved_code'):
                            print(f"[ML_AGENT] Generated improved code: {len(ml_improvement_payload['improved_code'])} chars")
                        else:
                            print(f"[ML_AGENT] No improved_code in payload. Keys: {list(ml_improvement_payload.keys())}")
                            if ml_improvement_payload.get('error'):
                                print(f"[ML_AGENT] Error: {ml_improvement_payload['error']}")
                    
                    # Capture final pipeline result
                    elif (event_data.get('agent') == 'pipeline' and 
                          event_data.get('status') == 'success'):
                        final_result = event_data.get('payload', {})
                        print(f"[PIPELINE] Pipeline completed")
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        # Analyze results
        print(f"\n[ANALYSIS] Results Analysis:")
        
        if ml_improvement_payload:
            print(f"[ML_PAYLOAD] ML Improvement payload keys: {list(ml_improvement_payload.keys())}")
            if ml_improvement_payload.get('error'):
                print(f"[ML_PAYLOAD] Error details: {ml_improvement_payload['error']}")
            if ml_improvement_payload.get('improved_code'):
                print(f"[ML_PAYLOAD] Improved code length: {len(ml_improvement_payload['improved_code'])} chars")
                print(f"[ML_PAYLOAD] First 200 chars: {ml_improvement_payload['improved_code'][:200]}...")
            if ml_improvement_payload.get('original_code'):
                print(f"[ML_PAYLOAD] Original code length: {len(ml_improvement_payload['original_code'])} chars")
        
        if final_result:
            print(f"[FINAL] Final result keys: {list(final_result.keys())}")
            if final_result.get('improved_code'):
                improved_code_list = final_result['improved_code']
                print(f"[FINAL] improved_code list length: {len(improved_code_list)}")
                if improved_code_list:
                    first_item = improved_code_list[0]
                    print(f"[FINAL] First improved_code item keys: {list(first_item.keys())}")
                    if first_item.get('improved_code'):
                        print(f"[FINAL] Improved code length: {len(first_item['improved_code'])} chars")
                        print(f"[FINAL] File path: {first_item.get('file_path', 'N/A')}")
                        print(f"[FINAL] Annotations count: {len(first_item.get('annotations', []))}")
            else:
                print(f"[FINAL] No improved_code in final result")
        
        print(f"\n[SUCCESS] Test completed!")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

if __name__ == "__main__":
    test_improved_code()