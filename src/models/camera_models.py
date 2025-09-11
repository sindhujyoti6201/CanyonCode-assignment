#!/usr/bin/env python3
"""
Camera-related Pydantic models
"""

from pydantic import BaseModel

class CameraFeedResponse(BaseModel):
    camera_id: str
    location: str
    region: str
    status: str
    clarity_score: float
    bandwidth_mbps: float
    storage_gb: float
    uptime_percentage: float
    encoder_config_id: str
    decoder_config_id: str
