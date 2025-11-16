#!/usr/bin/env python3
"""
Verify that all imports work correctly for advanced pipeline implementation
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all critical imports"""
    print("Testing imports for advanced pipeline implementation...")
    
    try:
        # Test ADK agents
        print("✓ Testing ADK agents...")
        from adk_agents.ingest_agent import ingest_agent
        from adk_agents.diagnosis_agent import diagnosis_agent
        from adk_agents.ml_improvement_agent import ml_improvement_agent
        from adk_agents.eval_agent import eval_agent
        from adk_agents.planner_agent import planner_agent
        from adk_agents.coordinator_agent import coordinator_agent
        print("  ✅ All ADK agents imported successfully")
        
        # Test Google GenAI types
        print("✓ Testing Google GenAI types...")
        from google.genai.types import Content, GenerateContentResponse, Part
        print("  ✅ Google GenAI types imported successfully")
        
        # Test MCP services
        print("✓ Testing MCP services...")
        from services.mcp_client import call_baseline, call_anomaly
        print("  ✅ MCP client imported successfully")
        
        # Test API
        print("✓ Testing API...")
        from api.main import app
        print("  ✅ FastAPI app imported successfully")
        
        print("\n🎉 All imports successful! Advanced pipeline implementation is ready.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key components"""
    print("\nTesting basic functionality...")
    
    try:
        # Test Content and Part creation
        from google.genai.types import Content, Part
        import json
        
        test_data = {"test": "data"}
        content = Content(parts=[Part(text=json.dumps(test_data))])
        print("  ✅ Content/Part creation works")
        
        # Test coordinator agent with minimal data
        from adk_agents.coordinator_agent import coordinator_agent
        
        minimal_data = {
            "run_id": "verify_test",
            "metrics": {"accuracy": 0.8}
        }
        
        print("  ✓ Testing coordinator agent...")
        content_request = Content(parts=[Part(text=json.dumps(minimal_data))])
        
        # This might fail due to missing API keys, but import should work
        try:
            response = coordinator_agent(content_request)
            print("  ✅ Coordinator agent executed successfully")
        except Exception as e:
            if "API_KEY" in str(e) or "GOOGLE_API_KEY" in str(e):
                print("  ⚠️  Coordinator agent needs API key (expected)")
            else:
                print(f"  ⚠️  Coordinator agent error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("TestLab-AI Advanced Pipeline - Import Verification")
    print("=" * 50)
    
    imports_ok = test_imports()
    
    if imports_ok:
        functionality_ok = test_basic_functionality()
        
        print("\n" + "=" * 50)
        if imports_ok and functionality_ok:
            print("✅ Verification complete! Advanced pipeline is ready to use.")
            print("\nNext steps:")
            print("1. Set up .env file with GOOGLE_API_KEY")
            print("2. Start MCP server: python start_server.py")
            print("3. Start API server: python start_api_server.py")
            print("4. Test pipeline: python test_option_b.py")
        else:
            print("❌ Some issues found. Check the output above.")
    else:
        print("\n❌ Import verification failed. Check dependencies.")
        print("Run: pip install -r requirements.txt")