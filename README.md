# TestLab-AI - Advanced Pipeline Implementation

**PIPELINE**: INGEST → DIAGNOSIS → ML_IMPROVEMENT → EVALUATION → PLANNER

A comprehensive ML experiment analysis pipeline that processes experiment data through multiple specialized agents to provide intelligent diagnosis, improvement recommendations, evaluation, and action planning.

## Architecture

### Pipeline Stages

1. **INGEST AGENT** - Normalizes experiment data (ML format or custom format)
2. **DIAGNOSIS AGENT** - Analyzes metrics, calls MCP tools (baseline_compare + anomaly_detect), detects issues
3. **ML_IMPROVEMENT AGENT** - Generates ML-specific improvement recommendations and action plans
4. **EVALUATION AGENT** - Evaluates current experiment state and performance
5. **PLANNER AGENT** - Creates comprehensive action plans based on all previous stages

### Coordinator Agent

The `coordinator_agent.py` orchestrates the entire pipeline, calling each agent in sequence and merging results into a comprehensive final report.

## Project Structure

```
TestLab-AI/
├── src/
│   ├── adk_agents/           # ADK-compliant agents
│   │   ├── ingest_agent.py
│   │   ├── diagnosis_agent.py
│   │   ├── ml_improvement_agent.py  # NEW - ML improvement suggestions
│   │   ├── eval_agent.py
│   │   ├── planner_agent.py
│   │   └── coordinator_agent.py     # Orchestrates full pipeline
│   ├── mcp_tools/            # MCP tools for baseline comparison and anomaly detection
│   ├── api/                  # FastAPI REST endpoints
│   │   └── main.py
│   ├── services/             # Support services
│   └── tests/                # Test files
├── examples/                 # Sample data files
├── start_api_server.py       # FastAPI server startup
├── start_server.py           # MCP server startup
├── test_option_b.py          # Pipeline test script
└── requirements.txt
```

## Key Features

### ADK Compliance
- All agents use `models/gemini-1.5-flash-001`
- Return `GenerateContentResponse` with `Content(parts=[Part(text="...")])`
- Structured JSON responses

### MCP Integration
- Diagnosis agent calls `baseline_compare` and `anomaly_detect` MCP tools
- Integrates MCP results into flags and recommendations
- Handles MCP service failures gracefully

### ML Improvement Agent
Returns structured recommendations:
```json
{
  "run_id": "...",
  "recommendations": [...],
  "action_plan": {
    "quick_fixes": [...],
    "medium_changes": [...],
    "long_term": [...]
  }
}
```

### Comprehensive Reporting
Final coordinator output includes:
```json
{
  "run_id": "...",
  "timestamps": {...},
  "ingest": {...},
  "diagnosis": {...},
  "ml_improvement": {...},
  "evaluation": {...},
  "planner": {...},
  "summary": {...}
}
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
GOOGLE_API_KEY=your_gemini_api_key
MCP_HOST=http://127.0.0.1:9000
```

## Usage

### Method 1: FastAPI REST API

1. Start the MCP server (for baseline/anomaly tools):
```bash
python start_server.py
```

2. Start the API server:
```bash
python start_api_server.py
```

3. Send POST request to `/run_pipeline`:
```bash
curl -X POST "http://127.0.0.1:8000/run_pipeline" \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "test_001",
    "model": "ResNet50",
    "hyperparameters": {"learning_rate": 0.001},
    "metrics": {"accuracy": 0.85, "train_loss": 0.2},
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

### Method 2: Direct Python Usage

```python
from adk_agents.coordinator_agent import coordinator_agent
from google.genai.types import Content, Part
import json

# Prepare experiment data
data = {
    "run_id": "test_001",
    "model": "ResNet50",
    "metrics": {"accuracy": 0.85, "train_loss": 0.2}
}

# Create request
request = Content(parts=[Part(text=json.dumps(data))])

# Run pipeline
response = coordinator_agent(request)

# Extract results
result = json.loads(response.candidates[0].content.parts[0].text)
```

### Method 3: Test Script

```bash
python test_option_b.py
```

## API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /run_pipeline` - Run full pipeline (structured input)
- `POST /run_pipeline_simple` - Run pipeline (raw JSON input)

## Input Formats

### ML Format
```json
{
  "run_id": "exp_001",
  "model": "ResNet50",
  "hyperparameters": {"learning_rate": 0.001},
  "metrics": {"accuracy": 0.85, "train_loss": 0.2},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Custom Format
```json
{
  "experiment_id": "test_001",
  "name": "Custom Experiment",
  "status": "completed",
  "results": {"passed": 85, "failed": 15},
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Development

### Running Tests
```bash
python -m pytest src/tests/
```

### Adding New Agents
1. Create agent file in `src/adk_agents/`
2. Follow ADK compliance patterns
3. Add to coordinator pipeline if needed
4. Create corresponding test file

## Configuration

### Thresholds (in diagnosis_agent.py)
- `overfit_pct`: 0.10 (10% validation loss increase)
- `fail_rate_warning`: 0.10 (10% test failure rate)
- `fail_rate_high`: 0.25 (25% test failure rate)

### Weights (for severity scoring)
- `critical`: 0.5
- `high`: 0.35
- `medium`: 0.15
- `mcp_anomaly`: 0.3
- `mcp_regression`: 0.4

## Troubleshooting

### Common Issues

1. **MCP Tools Unavailable**: Diagnosis agent handles MCP failures gracefully
2. **Gemini API Errors**: Check `GOOGLE_API_KEY` in `.env`
3. **Import Errors**: Ensure `src/` is in Python path

### Logs
- Coordinator agent prints stage progress
- Check console output for detailed execution info

## License

MIT License