"""
ML Improvement Agent (ADK-compliant)

Takes diagnosis + MCP baseline data, analyzes metrics, and suggests ML improvements.
Uses Gemini 1.5 Flash for intelligent recommendations.
"""

import json
import os
from typing import Any, Dict, List, Optional

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


def respond(obj: Any):
    """Helper to create ADK-compliant response"""
    txt = json.dumps(obj, indent=2)
    if genai:
        return GenerateContentResponse(candidates=[{"content": Content(parts=[Part(text=txt)])}])
    else:
        return {"candidates": [{"content": {"parts": [{"text": txt}]}}]}


def analyze_metrics_for_improvements(metrics: Dict[str, Any], flags: List[Dict], mcp_results: Dict) -> Dict[str, List[str]]:
    """Analyze metrics and flags to generate categorized improvement suggestions"""
    improvements = {
        "quick_fixes": [],
        "medium_changes": [],
        "long_term": []
    }
    
    # Analyze flags for specific improvements
    for flag in flags:
        code = flag.get("code", "")
        level = flag.get("level", "INFO")
        
        if "overfit" in code:
            if level == "HIGH":
                improvements["quick_fixes"].extend([
                    "Add dropout layers (0.2-0.5)",
                    "Implement early stopping with patience=5",
                    "Reduce learning rate by 50%"
                ])
                improvements["medium_changes"].extend([
                    "Implement data augmentation",
                    "Add L2 regularization (weight_decay=0.01)",
                    "Use cross-validation for model selection"
                ])
            else:
                improvements["medium_changes"].append("Monitor validation curves more closely")
        
        elif "underfit" in code:
            improvements["quick_fixes"].extend([
                "Increase model capacity (add layers/neurons)",
                "Increase learning rate by 2x",
                "Train for more epochs"
            ])
            improvements["medium_changes"].extend([
                "Feature engineering and selection",
                "Hyperparameter tuning (grid/random search)",
                "Try different model architectures"
            ])
        
        elif "unstable_metric" in code:
            improvements["quick_fixes"].extend([
                "Reduce learning rate",
                "Increase batch size",
                "Add gradient clipping (max_norm=1.0)"
            ])
            improvements["medium_changes"].append("Implement learning rate scheduling")
        
        elif "fail_rate" in code:
            improvements["quick_fixes"].extend([
                "Review failing test cases",
                "Add more validation checks",
                "Implement better error handling"
            ])
            improvements["long_term"].append("Comprehensive test suite redesign")
        
        elif "missing_artifact" in code:
            improvements["quick_fixes"].extend([
                "Configure model checkpointing",
                "Set up artifact storage",
                "Add model versioning"
            ])
    
    # Analyze MCP baseline results for regression improvements
    if mcp_results and mcp_results.get("baseline"):
        comparison = mcp_results["baseline"].get("comparison", {})
        for metric, info in comparison.items():
            z_score = info.get("z", 0)
            if abs(z_score) > 2.5:
                improvements["medium_changes"].append(f"Investigate {metric} regression (z-score: {z_score:.2f})")
                improvements["long_term"].append(f"Establish better baseline tracking for {metric}")
    
    # General improvements based on metrics
    success_rate = metrics.get("success_rate", 0)
    if success_rate < 0.9:
        improvements["medium_changes"].extend([
            "Implement ensemble methods",
            "Add model confidence scoring",
            "Improve data quality checks"
        ])
    
    # Remove duplicates while preserving order
    for category in improvements:
        improvements[category] = list(dict.fromkeys(improvements[category]))
    
    return improvements


def generate_llm_recommendations(diagnosis_data: Dict[str, Any]) -> List[str]:
    """Use Gemini to generate intelligent recommendations based on diagnosis"""
    
    prompt = f"""
    You are an ML expert analyzing experiment results. Based on the following diagnosis data, provide 3-5 specific, actionable recommendations for improving the ML system.

    Diagnosis Data:
    {json.dumps(diagnosis_data, indent=2)}

    Focus on:
    1. Performance improvements
    2. Stability enhancements  
    3. Best practices
    4. Specific technical solutions

    Return only a JSON array of recommendation strings, no other text.
    """
    
    try:
        if not model:
            return [
                "Install google-generativeai package for AI recommendations",
                "Review model architecture manually",
                "Check training logs for issues"
            ]
        response = model.generate_content(prompt)
        recommendations_text = response.text.strip()
        
        # Try to parse as JSON array
        if recommendations_text.startswith('[') and recommendations_text.endswith(']'):
            return json.loads(recommendations_text)
        else:
            # Fallback: split by lines and clean up
            lines = [line.strip() for line in recommendations_text.split('\n') if line.strip()]
            return lines[:5]  # Limit to 5 recommendations
            
    except Exception as e:
        # Fallback recommendations if LLM fails
        return [
            "Review model architecture for optimization opportunities",
            "Implement comprehensive monitoring and alerting",
            "Establish baseline performance benchmarks",
            "Add automated model validation pipeline",
            "Consider A/B testing for model improvements"
        ]


def ml_improvement_agent(request) -> GenerateContentResponse:
    """
    ML Improvement Agent - ADK Entry Point
    
    Input: Diagnosis results with metrics, flags, and MCP data
    Output: ML improvement recommendations and action plan
    """
    try:
        # Handle both Content object and direct dict input
        if hasattr(request, 'parts'):
            raw = request.parts[0].text
            data = json.loads(raw)
        else:
            data = request
        
        # Extract key components
        run_id = data.get("run_id", "unknown")
        metrics = data.get("raw_metrics", {})
        flags = data.get("flags", [])
        mcp_results = data.get("mcp_results", {})
        severity_score = data.get("severity_score_pct", 0)
        severity_label = data.get("severity_label", "LOW")
        
        # Generate categorized improvements
        action_plan = analyze_metrics_for_improvements(metrics, flags, mcp_results)
        
        # Generate LLM-powered recommendations
        llm_recommendations = generate_llm_recommendations({
            "metrics": metrics,
            "flags": flags[:3],  # Top 3 flags only for context
            "severity": {"score": severity_score, "label": severity_label}
        })
        
        # Combine all recommendations
        all_recommendations = []
        for category, items in action_plan.items():
            all_recommendations.extend(items)
        all_recommendations.extend(llm_recommendations)
        
        # Remove duplicates while preserving order
        unique_recommendations = list(dict.fromkeys(all_recommendations))
        
        # Prepare final output
        output = {
            "run_id": run_id,
            "recommendations": unique_recommendations,
            "action_plan": action_plan,
            "priority_score": min(100, severity_score + 10),  # Boost priority slightly
            "estimated_impact": {
                "quick_fixes": "High impact, low effort",
                "medium_changes": "Medium impact, medium effort", 
                "long_term": "High impact, high effort"
            },
            "next_steps": [
                "Implement quick fixes first",
                "Plan medium changes for next sprint",
                "Schedule long-term improvements",
                "Monitor impact of changes"
            ]
        }
        
        return respond(output)
        
    except Exception as e:
        return respond({"error": str(e), "run_id": "unknown"})