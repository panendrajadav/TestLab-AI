#!/usr/bin/env python3
"""
Test script to verify unique per-file improved code generation
"""

import requests
import json
import time

def test_multiple_unique_files():
    """Test that different models generate different improved code"""
    
    # Test Case 1: Low accuracy model
    test_data_a = {
        "run_id": f"model_a_{int(time.time())}",
        "model": "CNN Classifier A",
        "metrics": {
            "accuracy": 0.65,  # Low accuracy
            "loss": 0.8,
            "f1_score": 0.62
        }
    }
    
    # Test Case 2: High loss model  
    test_data_b = {
        "run_id": f"model_b_{int(time.time())}",
        "model": "LSTM Predictor B", 
        "metrics": {
            "accuracy": 0.85,
            "loss": 1.2,  # High loss
            "f1_score": 0.83
        }
    }
    
    print("[TEST] Testing Multiple Unique File Generation")
    print("=" * 60)
    
    results = {}
    
    for test_name, test_data in [("Model A (Low Accuracy)", test_data_a), ("Model B (High Loss)", test_data_b)]:
        print(f"\n[{test_name}] Testing: {test_data['model']}")
        print(f"[{test_name}] Metrics: accuracy={test_data['metrics']['accuracy']}, loss={test_data['metrics']['loss']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/run_pipeline_realtime",
                json=test_data,
                stream=True,
                headers={"Accept": "text/event-stream"}
            )
            
            if response.status_code != 200:
                print(f"[{test_name}] ERROR: Request failed: {response.status_code}")
                continue
            
            final_result = None
            
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    try:
                        event_data = json.loads(line[6:])
                        
                        if (event_data.get('agent') == 'pipeline' and 
                            event_data.get('status') == 'success'):
                            final_result = event_data.get('payload', {})
                            break
                            
                    except json.JSONDecodeError:
                        continue
            
            if final_result and final_result.get('improved_code'):
                improved_files = final_result['improved_code']
                results[test_name] = improved_files
                
                print(f"[{test_name}] SUCCESS: Generated {len(improved_files)} improved files")
                
                for i, file_info in enumerate(improved_files):
                    print(f"[{test_name}] File {i+1}:")
                    print(f"  - Path: {file_info.get('file_path', 'N/A')}")
                    print(f"  - Summary: {file_info.get('summary', 'N/A')}")
                    print(f"  - Code length: {len(file_info.get('improved_code', ''))} chars")
                    print(f"  - Annotations: {len(file_info.get('annotations', []))} items")
                    
                    # Show first annotation as example
                    if file_info.get('annotations'):
                        first_annotation = file_info['annotations'][0]
                        print(f"  - First improvement: Line {first_annotation.get('line', '?')} - {first_annotation.get('comment', 'N/A')}")
            else:
                print(f"[{test_name}] ERROR: No improved_code in final result")
                
        except Exception as e:
            print(f"[{test_name}] ERROR: {e}")
    
    # Compare results
    print(f"\n{'='*60}")
    print("[COMPARISON] Analyzing Uniqueness")
    
    if len(results) >= 2:
        model_names = list(results.keys())
        model_a_files = results[model_names[0]]
        model_b_files = results[model_names[1]]
        
        print(f"\n[UNIQUE] {model_names[0]} vs {model_names[1]}:")
        
        # Compare summaries
        summary_a = model_a_files[0].get('summary', '') if model_a_files else ''
        summary_b = model_b_files[0].get('summary', '') if model_b_files else ''
        
        print(f"  Summary A: '{summary_a}'")
        print(f"  Summary B: '{summary_b}'")
        print(f"  Summaries different: {summary_a != summary_b}")
        
        # Compare file paths
        path_a = model_a_files[0].get('file_path', '') if model_a_files else ''
        path_b = model_b_files[0].get('file_path', '') if model_b_files else ''
        
        print(f"  Path A: '{path_a}'")
        print(f"  Path B: '{path_b}'")
        print(f"  Paths different: {path_a != path_b}")
        
        # Compare code content (first 100 chars)
        code_a = model_a_files[0].get('improved_code', '')[:100] if model_a_files else ''
        code_b = model_b_files[0].get('improved_code', '')[:100] if model_b_files else ''
        
        print(f"  Code A (first 100 chars): '{code_a}...'")
        print(f"  Code B (first 100 chars): '{code_b}...'")
        print(f"  Code content different: {code_a != code_b}")
        
        # Overall uniqueness check
        is_unique = (summary_a != summary_b) or (path_a != path_b) or (code_a != code_b)
        print(f"\n[RESULT] Files are unique: {is_unique}")
        
        if is_unique:
            print("[SUCCESS] Different models generate different improved code!")
        else:
            print("[FAILURE] Models are generating identical improved code (BUG)")
    else:
        print("[ERROR] Could not compare - insufficient results")

if __name__ == "__main__":
    test_multiple_unique_files()