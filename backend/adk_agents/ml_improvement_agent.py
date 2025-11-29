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
            if z_score is not None and abs(z_score) > 2.5:
                improvements["medium_changes"].append(f"Investigate {metric} regression (z-score: {z_score:.2f})")
                improvements["long_term"].append(f"Establish better baseline tracking for {metric}")
    
    # General improvements based on metrics
    success_rate = metrics.get("success_rate", 0)
    if success_rate is not None and success_rate < 0.9:
        improvements["medium_changes"].extend([
            "Implement ensemble methods",
            "Add model confidence scoring",
            "Improve data quality checks"
        ])
    elif success_rate is None:
        # If no success rate, add general improvements
        improvements["medium_changes"].extend([
            "Implement comprehensive metrics tracking",
            "Add model performance monitoring",
            "Establish baseline performance metrics"
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


def generate_unique_improvements(diagnosis_data: Dict[str, Any], recommendations: List[str], run_id: str) -> List[Dict[str, Any]]:
    """Generate unique per-file improvements based on diagnosis data"""
    import uuid
    import difflib
    
    # Extract key info from diagnosis
    metrics = diagnosis_data.get("raw_metrics", {})
    flags = diagnosis_data.get("flags", [])
    model_name = diagnosis_data.get("model", "unknown_model")
    
    # Generate unique improvements based on actual diagnosis
    improvements = []
    
    # Determine file type and improvements based on metrics and flags
    if metrics.get("accuracy", 0) < 0.8:
        # Low accuracy - focus on model architecture
        file_path = f"models/{model_name.lower().replace(' ', '_')}_improved.py"
        
        # Generate specific improvements based on flags
        specific_improvements = []
        annotations = []
        
        for i, flag in enumerate(flags[:3]):  # Top 3 flags
            if "overfit" in flag.get("code", ""):
                specific_improvements.append("Added dropout layers")
                annotations.append({"line": 15 + i*5, "type": "add", "comment": f"Added dropout (rate=0.3) to prevent overfitting"})
            elif "missing_artifact" in flag.get("code", ""):
                specific_improvements.append("Added model checkpointing")
                annotations.append({"line": 45 + i*3, "type": "add", "comment": "Added automatic model checkpointing"})
            elif "unstable_metric" in flag.get("code", ""):
                specific_improvements.append("Added learning rate scheduling")
                annotations.append({"line": 25 + i*2, "type": "change", "comment": "Implemented ReduceLROnPlateau scheduler"})
        
        # Add metric-specific improvements
        if metrics.get("loss", 1.0) > 0.5:
            specific_improvements.append("Switched to Adam optimizer")
            annotations.append({"line": 35, "type": "change", "comment": "Changed from SGD to Adam optimizer with weight decay"})
        
        if len(specific_improvements) == 0:
            specific_improvements = ["Enhanced model architecture", "Added regularization"]
            annotations = [
                {"line": 20, "type": "add", "comment": "Added batch normalization layers"},
                {"line": 30, "type": "change", "comment": "Increased model capacity"}
            ]
        
        # Generate original code template
        original_code = f'''# Original {model_name} Model
import torch
import torch.nn as nn

class {model_name.replace(" ", "")}Model(nn.Module):
    def __init__(self, input_size=784, num_classes=10):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, num_classes)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

def train_model(model, train_loader):
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(10):
        for data, target in train_loader:
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
'''
        
        # Generate improved code with specific changes
        improved_code = f'''# Improved {model_name} Model - Run {run_id}
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim.lr_scheduler import ReduceLROnPlateau

class Improved{model_name.replace(" ", "")}Model(nn.Module):
    def __init__(self, input_size=784, num_classes=10, dropout_rate=0.3):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.bn1 = nn.BatchNorm1d(256)  # Added batch normalization
        self.dropout1 = nn.Dropout(dropout_rate)  # Added dropout for regularization
        self.fc2 = nn.Linear(256, 128)
        self.bn2 = nn.BatchNorm1d(128)
        self.dropout2 = nn.Dropout(dropout_rate)
        self.fc3 = nn.Linear(128, num_classes)
        
    def forward(self, x):
        x = F.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)
        x = F.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)
        return self.fc3(x)

def train_improved_model(model, train_loader, val_loader):
    # Switched to Adam optimizer with weight decay
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=0.01)
    scheduler = ReduceLROnPlateau(optimizer, patience=3)  # Added LR scheduling
    criterion = nn.CrossEntropyLoss()
    
    best_val_loss = float('inf')
    patience_counter = 0
    
    for epoch in range(50):
        # Training phase
        model.train()
        for data, target in train_loader:
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
        
        # Validation and checkpointing
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for data, target in val_loader:
                output = model(data)
                val_loss += criterion(output, target).item()
        
        val_loss /= len(val_loader)
        scheduler.step(val_loss)
        
        # Early stopping and model checkpointing
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), f'best_{model_name.lower()}_model.pth')
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= 5:
                break
'''
        
        # Generate diff
        diff = ''.join(difflib.unified_diff(
            original_code.splitlines(keepends=True),
            improved_code.splitlines(keepends=True),
            fromfile=f"original_{model_name.lower()}.py",
            tofile=f"improved_{model_name.lower()}.py",
            lineterm=""
        ))
        
        improvements.append({
            "pipeline_id": run_id,
            "file_path": file_path,
            "original_code": original_code,
            "improved_code": improved_code,
            "diff": diff,
            "annotations": annotations,
            "summary": ", ".join(specific_improvements[:3])  # Top 3 changes
        })
    
    return improvements


def generate_improved_code(diagnosis_data: Dict[str, Any], recommendations: List[str]) -> str:
    """Generate improved code based on diagnosis and recommendations"""
    
    prompt = f"""
    You are an ML expert. Based on the diagnosis and recommendations below, generate improved Python code that addresses the identified issues.

    Diagnosis Data:
    {json.dumps(diagnosis_data, indent=2)}

    Recommendations:
    {json.dumps(recommendations, indent=2)}

    Generate a complete, runnable Python code example that:
    1. Addresses the main issues found in diagnosis
    2. Implements the key recommendations
    3. Includes proper error handling and logging
    4. Uses modern ML best practices
    5. Is well-commented and production-ready

    Return only the Python code, no other text or markdown formatting.
    """
    
    try:
        if not model:
            return generate_fallback_improved_code(recommendations)
        
        response = model.generate_content(prompt)
        code = response.text.strip()
        
        # Clean up any markdown formatting
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]
        
        return code.strip()
        
    except Exception as e:
        return generate_fallback_improved_code(recommendations)


def generate_fallback_improved_code(recommendations: List[str]) -> str:
    """Generate fallback improved code when LLM is not available"""
    rec_comments = "\n".join(f"        # - {rec}" for rec in recommendations[:5])
    
    return f'''# Improved ML Pipeline Implementation
# Generated based on analysis recommendations

import logging
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from typing import Dict, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedMLPipeline:
    """Enhanced ML Pipeline with improvements based on diagnosis."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.metrics_history = []
        
        # Apply recommendations:
{rec_comments}
        
    def build_model(self) -> nn.Module:
        """Build improved model with regularization and proper architecture."""
        class ImprovedModel(nn.Module):
            def __init__(self, input_size, hidden_size, num_classes, dropout_rate=0.3):
                super().__init__()
                self.layers = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(dropout_rate),  # Prevent overfitting
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Dropout(dropout_rate),
                    nn.Linear(hidden_size // 2, num_classes)
                )
                
            def forward(self, x):
                return self.layers(x)
        
        model = ImprovedModel(
            input_size=self.config.get('input_size', 784),
            hidden_size=self.config.get('hidden_size', 256),
            num_classes=self.config.get('num_classes', 10),
            dropout_rate=self.config.get('dropout_rate', 0.3)
        )
        
        return model
    
    def train_with_improvements(self, train_loader: DataLoader, val_loader: DataLoader) -> Dict[str, Any]:
        """Enhanced training with early stopping and monitoring."""
        self.model = self.build_model()
        
        # Improved optimizer with weight decay for regularization
        optimizer = torch.optim.Adam(
            self.model.parameters(), 
            lr=self.config.get('learning_rate', 0.001),
            weight_decay=self.config.get('weight_decay', 0.01)
        )
        
        # Learning rate scheduler
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', patience=3, factor=0.5
        )
        
        criterion = nn.CrossEntropyLoss()
        
        # Early stopping parameters
        best_val_loss = float('inf')
        patience_counter = 0
        patience = self.config.get('patience', 5)
        
        training_history = {{
            'train_loss': [],
            'val_loss': [],
            'val_accuracy': []
        }}
        
        for epoch in range(self.config.get('max_epochs', 100)):
            # Training phase
            self.model.train()
            train_loss = 0.0
            
            for batch_idx, (data, target) in enumerate(train_loader):
                optimizer.zero_grad()
                output = self.model(data)
                loss = criterion(output, target)
                loss.backward()
                
                # Gradient clipping to prevent instability
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                optimizer.step()
                train_loss += loss.item()
            
            # Validation phase
            val_loss, val_accuracy = self.validate(val_loader, criterion)
            
            # Update learning rate
            scheduler.step(val_loss)
            
            # Record metrics
            training_history['train_loss'].append(train_loss / len(train_loader))
            training_history['val_loss'].append(val_loss)
            training_history['val_accuracy'].append(val_accuracy)
            
            logger.info(f"Epoch {{epoch+1}}: Train Loss={{train_loss/len(train_loader):.4f}}, "
                       f"Val Loss={{val_loss:.4f}}, Val Acc={{val_accuracy:.4f}}")
            
            # Early stopping check
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model checkpoint
                torch.save(self.model.state_dict(), 'best_model.pth')
            else:
                patience_counter += 1
                
            if patience_counter >= patience:
                logger.info(f"Early stopping at epoch {{epoch+1}}")
                break
        
        # Load best model
        self.model.load_state_dict(torch.load('best_model.pth'))
        
        return training_history
    
    def validate(self, val_loader: DataLoader, criterion) -> Tuple[float, float]:
        """Validation with comprehensive metrics."""
        self.model.eval()
        val_loss = 0.0
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for data, target in val_loader:
                output = self.model(data)
                val_loss += criterion(output, target).item()
                
                predictions = torch.argmax(output, dim=1)
                all_predictions.extend(predictions.cpu().numpy())
                all_targets.extend(target.cpu().numpy())
        
        val_loss /= len(val_loader)
        accuracy = accuracy_score(all_targets, all_predictions)
        
        return val_loss, accuracy
    
    def evaluate_comprehensive(self, test_loader: DataLoader) -> Dict[str, Any]:
        """Comprehensive evaluation with multiple metrics."""
        self.model.eval()
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for data, target in test_loader:
                output = self.model(data)
                predictions = torch.argmax(output, dim=1)
                all_predictions.extend(predictions.cpu().numpy())
                all_targets.extend(target.cpu().numpy())
        
        # Calculate comprehensive metrics
        accuracy = accuracy_score(all_targets, all_predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_targets, all_predictions, average='weighted'
        )
        
        metrics = {{
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'total_samples': len(all_targets)
        }}
        
        logger.info(f"Final Evaluation: {{metrics}}")
        return metrics

# Usage Example:
# config = {{
#     'input_size': 784,
#     'hidden_size': 256,
#     'num_classes': 10,
#     'learning_rate': 0.001,
#     'weight_decay': 0.01,
#     'dropout_rate': 0.3,
#     'patience': 5,
#     'max_epochs': 100
# }}
# 
# pipeline = ImprovedMLPipeline(config)
# history = pipeline.train_with_improvements(train_loader, val_loader)
# results = pipeline.evaluate_comprehensive(test_loader)
'''


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
        
        # Generate unique per-file improvements
        improved_files = generate_unique_improvements({
            "raw_metrics": metrics,
            "flags": flags,
            "severity_score_pct": severity_score,
            "severity_label": severity_label,
            "mcp_results": mcp_results,
            "model": data.get("model", "UnknownModel")
        }, unique_recommendations, run_id)
        
        # Generate original code for comparison (legacy)
        original_code = '''# Original ML Pipeline Implementation
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

class SimpleModel(nn.Module):
    def __init__(self, input_size=784, num_classes=10):
        super().__init__()
        self.fc = nn.Linear(input_size, num_classes)
        
    def forward(self, x):
        return self.fc(x)

def train_model(model, train_loader, epochs=10):
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(epochs):
        for data, target in train_loader:
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
    
    return model
'''
        
        # Prepare final output with unique improvements
        output = {
            "run_id": run_id,
            "recommendations": unique_recommendations,
            "action_plan": action_plan,
            "improved_files": improved_files,  # Array of per-file improvements
            "code_summary": f"Generated {len(improved_files)} improved files addressing {len(flags)} issues",
            "priority_score": min(100, severity_score + 10),
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
        
        # Legacy compatibility - extract first file's code
        if improved_files:
            output["improved_code"] = improved_files[0]["improved_code"]
            output["original_code"] = improved_files[0]["original_code"]
        else:
            # Fallback to generated code
            output["improved_code"] = generate_improved_code({
                "metrics": metrics,
                "flags": flags,
                "severity": {"score": severity_score, "label": severity_label},
                "mcp_results": mcp_results
            }, unique_recommendations)
            output["original_code"] = original_code
        
        return respond(output)
        
    except Exception as e:
        return respond({"error": str(e), "run_id": "unknown"})