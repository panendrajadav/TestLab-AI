#!/usr/bin/env python3
"""
FastAPI Server startup script for TestLab-AI Advanced Pipeline (Monorepo)

This starts the backend API server with:
- ML pipeline endpoints (/api/run_pipeline)
- Static frontend serving from ../dist/client
- CORS enabled for development and frontend
"""
import uvicorn
import sys
import os
from pathlib import Path

# Add current directory to path (backend agents are here, not in src/)
sys.path.insert(0, os.path.dirname(__file__))

# Try to enable CORS for frontend development
try:
    from fastapi.middleware.cors import CORSMiddleware
    from api.main import app
    
    # Configure CORS - allow frontend dev server and production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:8000",  # Backend itself
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("[INFO] CORS middleware configured for development")
except Exception as e:
    print(f"[WARN] Could not configure CORS: {e}")

if __name__ == "__main__":
    print("[INFO] Starting TestLab-AI Backend API Server...")
    print("[INFO] API endpoints: http://127.0.0.1:8000/api/")
    print("[INFO] Frontend: http://127.0.0.1:8000/ (after building frontend)")
    print("[INFO] Docs: http://127.0.0.1:8000/docs")
    print()
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)