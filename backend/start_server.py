#!/usr/bin/env python3
"""
MCP Server startup script
"""
import uvicorn
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    uvicorn.run("mcp_tools.mcp_server:app", host="127.0.0.1", port=9000, reload=True)