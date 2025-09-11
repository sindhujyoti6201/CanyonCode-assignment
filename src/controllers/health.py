#!/usr/bin/env python3
"""
Health Controller - Handles health check endpoints
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Camera Feed Query System API", "status": "running"}

@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Camera Feed Query System"}
