# TestLab-AI

ADK (Autonomous Discovery Kit) Ingest Agent for test experiment management and analysis.

## Project Structure

```
TestLab-AI/
├── .env                 # API keys (to be added)
├── .gitignore
├── README.md
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── adk_agents/
│   │   ├── __init__.py
│   │   └── ingest_agent.py          # ADK agent implementation
│   │
│   └── tests/
│       ├── __init__.py
│       └── test_ingest_adk.py       # Test runner
│
└── examples/
    └── sample_experiment_run.json   # Example input
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env` file

3. Run tests:
   ```bash
   pytest src/tests/
   ```

## Usage

See `examples/sample_experiment_run.json` for sample input format.
