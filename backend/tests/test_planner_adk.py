import json
import os
import sys

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.genai.types import Content
from adk_agents.planner_agent import planner_agent


def run_test(exp_file, diag_file=None):
    print(f"\n=== Running Planner Test: {exp_file} ===\n")

    if not os.path.exists(exp_file):
        print(f"ERROR: File not found: {exp_file}")
        return

    with open(exp_file, "r") as f:
        exp = json.load(f)

    payload = {"normalized": exp}

    if diag_file:
        if not os.path.exists(diag_file):
            print(f"ERROR: Diagnosis file not found: {diag_file}")
        else:
            with open(diag_file, "r") as d:
                payload["diagnosis"] = json.load(d)

    # Prepare ADK input
    content = Content(parts=[{"text": json.dumps(payload)}])

    # Call Planner Agent
    try:
        result = planner_agent(content)
        print("\n--- RAW AGENT OUTPUT ---")
        print(result)

        print("\n--- TEXT RESPONSE ---")
        print(result.candidates[0].content.parts[0].text)

    except Exception as e:
        print(f"\nERROR IN AGENT: {e}")


# -------------------------------------
# TEST 1 – Normal experiment + diagnosis
# -------------------------------------
run_test(
    "examples/sample_custom_experiment_normalized.json",
    "examples/sample_custom_diagnosis.json"
)

print("\n=== END OF TEST ===\n")
