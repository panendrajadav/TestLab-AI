import json
import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from agents.coordinator import CoordinatorAgent

# Load sample experiment JSON
with open("examples/sample_experiment_run.json") as f:
    exp = json.load(f)

# Initialize coordinator
coordinator = CoordinatorAgent()

# Process experiment
response = coordinator.process_experiment(exp)

print("\n=== TESTLAB AI OUTPUT ===")
print(json.dumps(response, indent=2))