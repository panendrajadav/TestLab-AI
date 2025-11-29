import json
from google.genai.types import Content
from adk_agents.ingest_agent import ingest_agent

def run_test(file):
    print(f"\n=== TESTING {file} ===")
    with open(file) as f:
        exp = json.load(f)

    input_content = Content(
        parts=[{"text": json.dumps(exp)}]
    )

    res = ingest_agent(input_content)
    print(res.output)

# ML format test
run_test("examples/sample_experiment_run.json")

# Custom format test
run_test("examples/sample_custom_experiment.json")
