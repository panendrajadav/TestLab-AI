#!/usr/bin/env python3
"""
Full Stack Startup Script for TestLab-AI
Starts both backend API server and frontend development server
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting Backend API Server...")
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Install backend dependencies if needed
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    except subprocess.CalledProcessError:
        print("⚠️  Failed to install backend dependencies")
    
    # Start the API server
    subprocess.run([
        "uvicorn", 
        "api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])

def run_frontend():
    """Start the React frontend development server"""
    print("🎨 Starting Frontend Development Server...")
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    # Install frontend dependencies if needed
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(["npm", "install"], check=True)
    
    # Start the development server
    subprocess.run(["npm", "run", "dev"])

def main():
    """Start both backend and frontend servers"""
    print("🔥 TestLab-AI Full Stack Startup")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    # Start frontend (this will block)
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n👋 Shutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()