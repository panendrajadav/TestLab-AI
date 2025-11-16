#!/usr/bin/env python3
"""
FastAPI Server startup script for TestLab-AI Advanced Pipeline
"""
import uvicorn
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)