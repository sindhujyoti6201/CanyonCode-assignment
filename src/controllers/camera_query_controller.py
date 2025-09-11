#!/usr/bin/env python3
"""
Camera Query Controller - Handles camera feed and query endpoints
"""

import os
import json
import time
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from models import QueryRequest, QueryResponse, CameraFeedResponse, SystemHealthResponse

router = APIRouter()

# Load camera data
def load_camera_data():
    """Load camera feed data from JSON file"""
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "camera_feeds.json")
    try:
        with open(data_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Camera data file not found")

# Load data on startup
camera_data = load_camera_data()

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language queries about camera feeds"""
    start_time = time.time()
    query = request.query.lower()
    
    try:
        # Simple query processing
        if "pacific" in query and "clarity" in query:
            pacific_cameras = [c for c in camera_data if c["region"].lower() == "pacific"]
            if pacific_cameras:
                best_camera = max(pacific_cameras, key=lambda x: x["clarity_score"])
                response = f"Camera {best_camera['camera_id']} in {best_camera['location']} has the best clarity in the Pacific region with a score of {best_camera['clarity_score']}."
            else:
                response = "No Pacific region cameras found."
        elif "bandwidth" in query and "high" in query:
            high_bandwidth = [c for c in camera_data if c["bandwidth_mbps"] > 10]
            if high_bandwidth:
                camera_list = ", ".join([c["camera_id"] for c in high_bandwidth])
                response = f"Cameras with high bandwidth usage: {camera_list}"
            else:
                response = "No cameras with high bandwidth usage found."
        elif "system health" in query or "health" in query:
            active_cameras = len([c for c in camera_data if c["status"] == "active"])
            total_cameras = len(camera_data)
            health_score = (active_cameras / total_cameras * 100) if total_cameras > 0 else 0
            response = f"System Health: {active_cameras}/{total_cameras} cameras active, {health_score:.1f}% health score."
        else:
            response = f"I understand you're asking about: '{request.query}'. Please rephrase your question or try a different query."
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            response=response,
            query_type="processed",
            execution_time=execution_time,
            metadata={"processed_at": "2024-01-01T00:00:00Z"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/cameras", response_model=List[CameraFeedResponse])
async def get_cameras(
    region: Optional[str] = Query(None, description="Filter by region"),
    status: Optional[str] = Query(None, description="Filter by status"),
    min_clarity: Optional[float] = Query(None, description="Minimum clarity score")
):
    """Get camera feeds with optional filtering"""
    try:
        filtered_data = camera_data.copy()
        
        if region:
            filtered_data = [c for c in filtered_data if c["region"].lower() == region.lower()]
        
        if status:
            filtered_data = [c for c in filtered_data if c["status"].lower() == status.lower()]
        
        if min_clarity is not None:
            filtered_data = [c for c in filtered_data if c["clarity_score"] >= min_clarity]
        
        return filtered_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cameras: {str(e)}")

@router.get("/cameras/{camera_id}")
async def get_camera_details(camera_id: str):
    """Get detailed information about a specific camera"""
    try:
        camera = next((c for c in camera_data if c["camera_id"] == camera_id), None)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        return camera
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving camera details: {str(e)}")

@router.get("/regions")
async def get_regions():
    """Get list of all available regions"""
    try:
        regions = list(set(c["region"] for c in camera_data))
        return {"regions": regions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving regions: {str(e)}")

@router.get("/statistics")
async def get_statistics():
    """Get system statistics and summary information"""
    try:
        regions = {}
        statuses = {}
        
        for camera in camera_data:
            region = camera["region"]
            status = camera["status"]
            
            regions[region] = regions.get(region, 0) + 1
            statuses[status] = statuses.get(status, 0) + 1
        
        return {
            "total_cameras": len(camera_data),
            "region_distribution": regions,
            "status_distribution": statuses,
            "average_clarity": sum(c["clarity_score"] for c in camera_data) / len(camera_data) if camera_data else 0,
            "average_bandwidth": sum(c["bandwidth_mbps"] for c in camera_data) / len(camera_data) if camera_data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health():
    """Get system health status"""
    try:
        active_cameras = len([c for c in camera_data if c["status"] == "active"])
        error_cameras = len([c for c in camera_data if c["status"] == "error"])
        avg_uptime = sum(c["uptime_percentage"] for c in camera_data) / len(camera_data) if camera_data else 0
        health_score = (active_cameras / len(camera_data) * 100) if camera_data else 0
        
        return SystemHealthResponse(
            health_score=health_score,
            total_cameras=len(camera_data),
            active_cameras=active_cameras,
            error_cameras=error_cameras,
            uptime_percentage=avg_uptime,
            status="healthy" if health_score > 80 else "degraded"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving health status: {str(e)}")

@router.get("/search")
async def search_cameras(q: str = Query(..., description="Search query")):
    """Search cameras by query string"""
    try:
        query_lower = q.lower()
        results = []
        
        for camera in camera_data:
            if (query_lower in camera["camera_id"].lower() or 
                query_lower in camera["location"].lower() or 
                query_lower in camera["region"].lower()):
                results.append(camera)
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching cameras: {str(e)}")
