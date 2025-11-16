import json
import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, src_path)

# Import the diagnosis agent
try:
    from adk_agents.diagnosis_agent import diagnosis_agent
    print("Successfully imported diagnosis_agent")
except ImportError as e:
    print(f"diagnosis_agent import failed: {e}")
    def diagnosis_agent(data):
        # Simple mock response
        return type('Result', (), {
            'candidates': [type('Candidate', (), {
                'content': type('Content', (), {
                    'parts': [type('Part', (), {'text': f"Diagnosed: {data}"})()]
                })()
            })()]
        })()

def run_test(file):
    print(f"\n=== TEST {file} ===")
    try:
        with open(file) as f:
            data = json.load(f)
        
        # Simple diagnosis without Google GenAI
        res = diagnosis_agent(data)
        print("OUTPUT:")
        # Handle both real and mock responses
        if hasattr(res, 'candidates') and res.candidates:
            print(res.candidates[0].content.parts[0].text)
        else:
            print(res)
    except FileNotFoundError:
        print(f"File not found: {file}")
    except Exception as e:
        print(f"Error: {e}")

# Run tests on available samples
run_test(os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'sample_experiment_run.json'))
run_test(os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'sample.json'))
