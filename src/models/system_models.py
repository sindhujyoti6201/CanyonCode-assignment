#!/usr/bin/env python3
"""
System-related Pydantic models
"""

from pydantic import BaseModel

class SystemHealthResponse(BaseModel):
    health_score: float
    total_cameras: int
    active_cameras: int
    error_cameras: int
    uptime_percentage: float
    status: str
