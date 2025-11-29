#!/usr/bin/env python3
"""
Test architecture detection and specific improvements
"""

import requests
import json
import time

def test_architecture_specific_improvements():
    """Test that different architectures get appropriate improvements"""
    
    test_cases = [
        {
            "name": "CNN Model",
            "data": {
                "run_id": f"cnn_test_{int(time.time())}",
                "model": "ResNet CNN Classifier",
                "metrics": {"accuracy": 0.65, "loss": 0.8}
            },
            "expected_improvements": ["BatchNorm2d", "Dropout2d", "AdamW"]
        },
        {
            "name": "MLP Model", 
            "data": {
                "run_id": f"mlp_test_{int(time.time())}",
                "model": "Dense MLP Network",
                "metrics": {"accuracy": 0.70, "loss": 0.6}
            },
            "expected_improvements": ["BatchNorm1d", "Dropout", "AdamW"]
        },
        {
            "name": "Transformer Model",
            "data": {
                "run_id": f"transformer_test_{int(time.time())}",
                "model": "BERT Transformer",
                "metrics": {"accuracy": 0.80, "loss": 0.4}
            },
            "expected_improvements": ["LayerNorm", "attention dropout", "CosineAnnealingLR"]
        }
    ]
    
    print("[TEST] Testing Architecture-Specific Improvements")
    print("=" * 60)
    
    results = {}
    
    for test_case in test_cases:
        name = test_case["name"]
        data = test_case["data"]
        expected = test_case["expected_improvements"]
        
        print(f"\n[{name}] Testing: {data['model']}")
        print(f"[{name}] Expected improvements: {', '.join(expected)}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/run_pipeline_realtime",
                json=data,
                stream=True,
                headers={"Accept": "text/event-stream"}
            )
            
            if response.status_code != 200:
                print(f"[{name}] ERROR: Request failed: {response.status_code}")
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
                results[name] = improved_files
                
                print(f"[{name}] SUCCESS: Generated {len(improved_files)} improved files")
                
                for i, file_info in enumerate(improved_files):
                    print(f"[{name}] File {i+1}:")
                    print(f"  - Path: {file_info.get('file_path', 'N/A')}")
                    print(f"  - Summary: {file_info.get('summary', 'N/A')}")
                    
                    # Check for expected improvements in code
                    improved_code = file_info.get('improved_code', '')
                    annotations = file_info.get('annotations', [])
                    
                    found_improvements = []
                    for exp in expected:
                        if (exp.lower() in improved_code.lower() or 
                            any(exp.lower() in ann.get('comment', '').lower() for ann in annotations)):
                            found_improvements.append(exp)
                    
                    print(f"  - Expected improvements found: {found_improvements}")
                    print(f"  - Architecture detection: {'✓' if found_improvements else '✗'}")
                    
                    # Show annotations
                    if annotations:
                        print(f"  - Key annotations:")
                        for ann in annotations[:3]:
                            print(f"    * Line {ann.get('line', '?')}: {ann.get('comment', 'N/A')}")
            else:
                print(f"[{name}] ERROR: No improved_code in final result")
                
        except Exception as e:
            print(f"[{name}] ERROR: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("[SUMMARY] Architecture Detection Results")
    
    for name, files in results.items():
        if files:
            file_info = files[0]
            path = file_info.get('file_path', '')
            summary = file_info.get('summary', '')
            
            # Determine detected architecture from path
            if 'cnn' in path.lower():
                detected = 'CNN'
            elif 'mlp' in path.lower():
                detected = 'MLP'
            elif 'transformer' in path.lower():
                detected = 'Transformer'
            else:
                detected = 'Unknown'
            
            print(f"\n[{name}]:")
            print(f"  Detected Architecture: {detected}")
            print(f"  File Path: {path}")
            print(f"  Summary: {summary}")
            print(f"  Architecture-Appropriate: {'✓' if detected.lower() in name.lower() else '✗'}")

if __name__ == "__main__":
    test_architecture_specific_improvements()