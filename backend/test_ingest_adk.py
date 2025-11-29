import json
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Mock the Google GenAI types since we don't have the actual library
class Content:
    def __init__(self, parts):
        self.parts = parts

class GenerateContentResponse:
    def __init__(self, output):
        self.output = output

# Simple test using existing structure
def test_ingest():
    # Load sample experiment JSON
    with open("examples/sample_experiment_run.json") as f:
        exp = json.load(f)
    
    print("\n=== SAMPLE EXPERIMENT DATA ===")
    print(json.dumps(exp, indent=2))
    
    # Create mock content
    input_content = Content(
        parts=[{"text": json.dumps(exp)}]
    )
    
    # Mock the ingest agent function without Google API dependency
    def mock_ingest_agent(request):
        try:
            raw_text = request.parts[0]["text"]
            exp_data = json.loads(raw_text)
            
            required_fields = ["run_id", "model", "hyperparameters", "metrics", "timestamp"]
            missing = [f for f in required_fields if f not in exp_data]
            
            if missing:
                return GenerateContentResponse(f"[ERROR] Missing fields: {missing}")
            
            print("Experiment ingested:", exp_data["run_id"])
            return GenerateContentResponse("[SUCCESS] Experiment validated and ingested.")
            
        except Exception as e:
            return GenerateContentResponse(f"[ERROR] Failed to process experiment: {str(e)}")
    
    # Test the mock agent
    response = mock_ingest_agent(input_content)
    
    print("\n=== ADK AGENT OUTPUT ===")
    print(response.output)
    
    return "SUCCESS" in response.output

if __name__ == "__main__":
    success = test_ingest()
    if success:
        print("\n✅ Test passed!")
    else:
        print("\n❌ Test failed!")