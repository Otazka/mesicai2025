#!/usr/bin/env python3
"""
Simplified backend server for testing
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create a simple FastAPI app
app = FastAPI(title="AI Skills Development Chatbot - Simple Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Skills Development Chatbot API - Simple Version",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "simple"}

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "API is working!", "data": "test"}

if __name__ == "__main__":
    print("🚀 Starting simple backend server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health")
    print("🧪 Test endpoint: http://localhost:8000/api/test")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
