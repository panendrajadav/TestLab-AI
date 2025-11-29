#!/bin/bash
# Test SSE pipeline with curl

echo "[TEST] Testing Event-Driven Pipeline with curl"
echo "[SSE] Connecting to SSE stream..."
echo

curl -N -H "Accept: text/event-stream" \
     -H "Content-Type: application/json" \
     -X POST \
     -d '{
       "run_id": "curl_test_'$(date +%s)'",
       "model": "Curl Test Model", 
       "metrics": {
         "accuracy": 0.78,
         "loss": 0.42,
         "f1_score": 0.75
       },
       "hyperparameters": {
         "learning_rate": 0.001,
         "batch_size": 32,
         "epochs": 50
       }
     }' \
     http://localhost:8000/api/run_pipeline_realtime

echo
echo "[DONE] SSE stream completed"