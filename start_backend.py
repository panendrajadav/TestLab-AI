#!/usr/bin/env python3
"""
Simple backend startup script for TestLab-AI
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the FastAPI backend server"""
    print("Starting TestLab-AI Backend Server...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
    
    # Start the server
    print("Starting server on http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    print("Health check at http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([
            "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == "__main__":
    main()