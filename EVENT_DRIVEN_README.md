# Event-Driven Pipeline Implementation

This document describes the changes made to implement event-driven pipeline behavior in TestLab-AI.

## Changes Made

### Backend Changes

1. **New SSE Endpoint**: `/api/run_pipeline_realtime` now provides structured agent events
2. **Agent Event Protocol**: Each agent emits structured messages with:
   ```json
   {
     "agent": "ingest_agent",
     "status": "started|processing|success|failed", 
     "timestamp": "2024-01-01T12:00:00.000Z",
     "payload": { /* optional: results, metrics, improved_code */ },
     "error": "<error message if failed>"
   }
   ```

### Frontend Changes

1. **Removed Speed Slider**: No more artificial time-based progression
2. **Event-Driven Progression**: Steps advance only after real agent completion
3. **Real-time Tab Updates**: Overview, JSON, Logs, and Improved Code populate as data arrives
4. **Error Handling**: Failed agents show retry/skip options

### Key Features

- **Real-time Updates**: All tabs update immediately when agents complete
- **True Event-Driven**: No timers - progression waits for actual agent success/failure
- **Error Recovery**: Retry failed agents or skip to continue pipeline
- **Structured Logging**: Timestamped logs with agent status and messages

## Testing

### Start Backend
```bash
cd backend
python -m uvicorn api.main:app --reload --port 8000
```

### Start Frontend  
```bash
cd frontend
npm run dev
```

### Test SSE Events
```bash
python test_sse.py
```

## Expected Behavior

1. **Pipeline Start**: Click "Run Pipeline" - no speed control visible
2. **Agent Progression**: Each step waits for real agent completion
3. **Real-time Logs**: See timestamped agent events as they happen
4. **Tab Updates**: Overview/JSON/Improved Code populate when data is available
5. **Error Handling**: Failed agents pause pipeline with retry/skip options

## Acceptance Criteria ✅

- ✅ Speed slider removed
- ✅ Steps advance only after agent success events  
- ✅ Logs stream in real-time with timestamps
- ✅ Overview tab shows metrics when available
- ✅ JSON tab displays pipeline structure
- ✅ Improved Code tab populates after ML agent success
- ✅ Agent failures pause pipeline with retry/skip options
- ✅ SSE test script validates event format

## API Endpoints

- `POST /api/run_pipeline_realtime` - Event-driven pipeline with SSE
- `GET /api/health` - Health check
- `GET /api/pipeline/stream/{pipeline_id}` - Generic SSE endpoint (future use)

## Event Flow

```
1. Server Started → 2. Coordinator → 3. Ingest Agent → 4. Diagnosis Agent 
→ 5. ML Improvement Agent → 6. Evaluation Agent → 7. Planner Agent → 8. Complete
```

Each agent emits: `started` → `processing` → `success`/`failed`

Frontend advances to next step only on `success` status.