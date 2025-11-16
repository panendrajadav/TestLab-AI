import json
import os
from dotenv import load_dotenv
try:
    import google.generativeai as genai
    from google.genai.types import Content, GenerateContentResponse, Part
except ImportError:
    genai = None
    Content = dict
    GenerateContentResponse = dict
    Part = dict

load_dotenv()

# Configure Gemini
if genai:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-pro")
else:
    model = None

def adk_response(text: str):
    """ADK-compliant response wrapper"""
    if genai:
        return GenerateContentResponse(
            candidates=[{
                "content": Content(parts=[Part(text=text)])
            }]
        )
    else:
        return {"candidates": [{"content": {"parts": [{"text": text}]}}]}

def extract_flag_text(flag):
    """Extract searchable text from flag dict or string"""
    if isinstance(flag, dict):
        code = flag.get("code", "")
        message = flag.get("message", "")
        return f"{code} {message}".lower()
    return str(flag).lower()

def generate_rule_based_suggestions(flags):
    """Generate rule-based suggestions from diagnosis flags"""
    suggestions = []
    
    for flag in flags:
        flag_text = extract_flag_text(flag)
        
        if "missing_artifact" in flag_text or "checkpoint" in flag_text:
            suggestions.append("Configure model checkpointing in your training pipeline")
            
        if "high_fail_rate" in flag_text or "test" in flag_text:
            suggestions.append("Review failing test cases and fix underlying issues")
            
        if "overfit" in flag_text:
            suggestions.append("Add regularization (dropout, L2) or reduce model complexity")
            
        if "variance" in flag_text or "unstable" in flag_text:
            suggestions.append("Increase training stability with learning rate scheduling")
            
        if "spike" in flag_text or "anomaly" in flag_text:
            suggestions.append("Investigate training logs for data or infrastructure issues")
    
    return suggestions if suggestions else ["No specific issues detected - continue monitoring"]

def planner_agent(request) -> GenerateContentResponse:
    try:
        # Handle both dict and Content object inputs
        if isinstance(request, dict):
            data = request
        elif hasattr(request, 'parts'):
            raw_text = request.parts[0].text
            data = json.loads(raw_text)
        else:
            data = json.loads(str(request))

        # Extract diagnosis info
        run_id = data.get("run_id", "unknown")
        severity = data.get("severity_score", 0)
        flags = data.get("flags", [])
        
        # Generate rule-based suggestions
        rule_suggestions = generate_rule_based_suggestions(flags)
        
        # Prepare LLM enhancement prompt
        flag_summary = []
        for flag in flags:
            if isinstance(flag, dict):
                flag_summary.append(f"- {flag.get('code', 'unknown')}: {flag.get('message', 'no message')}")
            else:
                flag_summary.append(f"- {flag}")
        
        flag_text = "\n".join(flag_summary) if flag_summary else "No issues detected"
        
        # Call Gemini for enhanced planning
        llm_prompt = f"""
Based on this ML experiment diagnosis:

Run ID: {run_id}
Severity Score: {severity}/100
Issues Found:
{flag_text}

Rule-based suggestions:
{chr(10).join(f"- {s}" for s in rule_suggestions)}

Provide an enhanced improvement plan with:
1. Priority ranking of actions
2. Specific implementation steps
3. Expected outcomes

Keep response concise and actionable.
"""
        
        try:
            if model:
                llm_response = model.generate_content(llm_prompt)
                llm_plan = llm_response.text if hasattr(llm_response, 'text') else "LLM enhancement unavailable"
            else:
                llm_plan = "LLM unavailable (missing google-generativeai)"
        except Exception as e:
            llm_plan = f"LLM enhancement failed: {str(e)}"
        
        # Compile final plan
        plan_result = {
            "run_id": run_id,
            "severity_score": severity,
            "rule_based_suggestions": rule_suggestions,
            "llm_enhanced_plan": llm_plan,
            "flags_analyzed": len(flags),
            "priority": "high" if severity > 50 else "medium" if severity > 20 else "low"
        }
        
        return adk_response(json.dumps(plan_result, indent=2))
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Planning failed: {str(e)}"
        }
        return adk_response(json.dumps(error_result, indent=2))