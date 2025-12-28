#!/usr/bin/env python3
"""
VoRAG Backend - Main entry point
Run with: python3 main.py
"""

import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting VoRAG Backend...")
    print("📍 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("❤️  Health: http://localhost:8000/health")
    print("\n✋ Press CTRL+C to stop\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
