import json
import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, src_path)
print(f"Added to path: {src_path}")

# Import the eval agent
try:
    from adk_agents.eval_agent import eval_agent
    print("Successfully imported eval_agent")
except ImportError as e:
    print(f"eval_agent import failed: {e}")
    def eval_agent(data):
        return type('Result', (), {'output': f"Evaluated: {data}"})()  # Simple mock

def run(file):
    print(f"\n=== TEST {file} ===")
    try:
        with open(file) as f:
            obj = json.load(f)
        
        # Simple evaluation without Google GenAI
        res = eval_agent(obj)
        print("OUTPUT:")
        print(res.output if hasattr(res, 'output') else res)
    except FileNotFoundError:
        print(f"File not found: {file}")
    except Exception as e:
        print(f"Error: {e}")

# Test on the normalized ML sample you have
run(os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'sample.json'))

# Test on other samples if they exist
run(os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'sample_experiment_run.json'))
