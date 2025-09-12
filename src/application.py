#!/usr/bin/env python3
"""
Camera Feed Query System - FastAPI Server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from controllers.health import router as health_router
from controllers.chatbot_controller import router as chatbot_router

# Initialize FastAPI app
app = FastAPI(
    title="Camera Feed Query System",
    description="AI-Powered Natural Language Query Interface for Camera Feeds",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(chatbot_router, prefix="/api/v1", tags=["chatbot"])

if __name__ == "__main__":
    print("Starting API server on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
