"""
MCP Tools for Data Analysis Operations
Provides tools for analyzing camera feed data, performance metrics, and insights
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta
import statistics

class AnalysisTools:
    """MCP Tools for analyzing camera feed data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "camera_feeds.db"
    
    def get_top_cameras_by_clarity(self, region: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get cameras with highest clarity scores"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = "SELECT * FROM camera_feeds WHERE 1=1"
        params = []
        
        if region:
            query += " AND region = ?"
            params.append(region)
        
        query += " ORDER BY clarity_score DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_performance_analysis(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Analyze performance metrics by region or overall"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT clarity_score, bandwidth_usage, storage_usage FROM camera_feeds WHERE 1=1"
        params = []
        
        if region:
            query += " AND region = ?"
            params.append(region)
        
        cursor = conn.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            return {"error": "No data found"}
        
        clarity_scores = [row[0] for row in data]
        bandwidth_usage = [row[1] for row in data]
        storage_usage = [row[2] for row in data]
        
        return {
            "clarity_analysis": {
                "mean": round(statistics.mean(clarity_scores), 2),
                "median": round(statistics.median(clarity_scores), 2),
                "std_dev": round(statistics.stdev(clarity_scores), 2),
                "min": min(clarity_scores),
                "max": max(clarity_scores)
            },
            "bandwidth_analysis": {
                "mean_mbps": round(statistics.mean(bandwidth_usage), 2),
                "median_mbps": round(statistics.median(bandwidth_usage), 2),
                "total_mbps": round(sum(bandwidth_usage), 2)
            },
            "storage_analysis": {
                "mean_gb": round(statistics.mean(storage_usage), 2),
                "median_gb": round(statistics.median(storage_usage), 2),
                "total_gb": round(sum(storage_usage), 2)
            },
            "sample_size": len(data)
        }
    
    def get_region_comparison(self) -> Dict[str, Any]:
        """Compare performance across different regions"""
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute("""
            SELECT region, 
                   COUNT(*) as camera_count,
                   AVG(clarity_score) as avg_clarity,
                   AVG(bandwidth_usage) as avg_bandwidth,
                   AVG(storage_usage) as avg_storage,
                   SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_cameras
            FROM camera_feeds 
            GROUP BY region
            ORDER BY avg_clarity DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "region": row[0],
                "camera_count": row[1],
                "average_clarity": round(row[2], 2),
                "average_bandwidth_mbps": round(row[3], 2),
                "average_storage_gb": round(row[4], 2),
                "active_cameras": row[5],
                "uptime_percentage": round((row[5] / row[1]) * 100, 2)
            })
        
        conn.close()
        return {"region_comparison": results}
    
    def get_encoder_decoder_analysis(self) -> Dict[str, Any]:
        """Analyze encoder and decoder configuration usage"""
        conn = sqlite3.connect(self.db_path)
        
        # Encoder analysis
        encoder_cursor = conn.execute("""
            SELECT ep.id, ep.resolution, ep.codec, ep.bitrate,
                   COUNT(cf.camera_id) as usage_count,
                   AVG(cf.clarity_score) as avg_clarity
            FROM encoder_parameters ep
            LEFT JOIN camera_feeds cf ON ep.id = cf.encoder_config_id
            GROUP BY ep.id
            ORDER BY usage_count DESC
        """)
        
        encoder_analysis = []
        for row in encoder_cursor.fetchall():
            encoder_analysis.append({
                "config_id": row[0],
                "resolution": row[1],
                "codec": row[2],
                "bitrate_kbps": row[3],
                "usage_count": row[4],
                "average_clarity": round(row[5], 2) if row[5] else 0
            })
        
        # Decoder analysis
        decoder_cursor = conn.execute("""
            SELECT dp.id, dp.output_format, dp.hardware_acceleration, dp.thread_count,
                   COUNT(cf.camera_id) as usage_count,
                   AVG(cf.clarity_score) as avg_clarity
            FROM decoder_parameters dp
            LEFT JOIN camera_feeds cf ON dp.id = cf.decoder_config_id
            GROUP BY dp.id
            ORDER BY usage_count DESC
        """)
        
        decoder_analysis = []
        for row in decoder_cursor.fetchall():
            decoder_analysis.append({
                "config_id": row[0],
                "output_format": row[1],
                "hardware_acceleration": bool(row[2]),
                "thread_count": row[3],
                "usage_count": row[4],
                "average_clarity": round(row[5], 2) if row[5] else 0
            })
        
        conn.close()
        
        return {
            "encoder_analysis": encoder_analysis,
            "decoder_analysis": decoder_analysis
        }
    
    def get_bandwidth_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Suggest bandwidth optimization opportunities"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Find cameras with high bandwidth usage but low clarity
        cursor = conn.execute("""
            SELECT cf.*, ep.bitrate, ep.resolution, ep.codec
            FROM camera_feeds cf
            JOIN encoder_parameters ep ON cf.encoder_config_id = ep.id
            WHERE cf.bandwidth_usage > 10 AND cf.clarity_score < 80
            ORDER BY cf.bandwidth_usage DESC
        """)
        
        suggestions = []
        for row in cursor.fetchall():
            suggestions.append({
                "camera_id": row["camera_id"],
                "location": row["location"],
                "region": row["region"],
                "current_bandwidth_mbps": row["bandwidth_usage"],
                "current_clarity": row["clarity_score"],
                "current_bitrate_kbps": row["bitrate"],
                "current_resolution": row["resolution"],
                "current_codec": row["codec"],
                "suggestion": "Consider reducing bitrate or resolution to optimize bandwidth usage",
                "potential_savings_mbps": round(row["bandwidth_usage"] * 0.3, 2)
            })
        
        conn.close()
        return suggestions
    
    def get_clarity_improvement_opportunities(self) -> List[Dict[str, Any]]:
        """Identify cameras that could benefit from clarity improvements"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Find cameras with low clarity but good bandwidth availability
        cursor = conn.execute("""
            SELECT cf.*, ep.bitrate, ep.resolution, ep.codec
            FROM camera_feeds cf
            JOIN encoder_parameters ep ON cf.encoder_config_id = ep.id
            WHERE cf.clarity_score < 75 AND cf.bandwidth_usage < 8
            ORDER BY cf.clarity_score ASC
        """)
        
        opportunities = []
        for row in cursor.fetchall():
            opportunities.append({
                "camera_id": row["camera_id"],
                "location": row["location"],
                "region": row["region"],
                "current_clarity": row["clarity_score"],
                "current_bandwidth_mbps": row["bandwidth_usage"],
                "current_bitrate_kbps": row["bitrate"],
                "current_resolution": row["resolution"],
                "current_codec": row["codec"],
                "suggestion": "Consider upgrading to higher bitrate or resolution for better clarity",
                "estimated_improvement": "15-25% clarity improvement possible"
            })
        
        conn.close()
        return opportunities
    
    def get_health_status_report(self) -> Dict[str, Any]:
        """Generate overall system health report"""
        conn = sqlite3.connect(self.db_path)
        
        # Overall statistics
        total_cameras = conn.execute("SELECT COUNT(*) FROM camera_feeds").fetchone()[0]
        active_cameras = conn.execute("SELECT COUNT(*) FROM camera_feeds WHERE status = 'active'").fetchone()[0]
        error_cameras = conn.execute("SELECT COUNT(*) FROM camera_feeds WHERE status = 'error'").fetchone()[0]
        maintenance_cameras = conn.execute("SELECT COUNT(*) FROM camera_feeds WHERE status = 'maintenance'").fetchone()[0]
        
        # Performance metrics
        avg_clarity = conn.execute("SELECT AVG(clarity_score) FROM camera_feeds WHERE status = 'active'").fetchone()[0]
        total_bandwidth = conn.execute("SELECT SUM(bandwidth_usage) FROM camera_feeds WHERE status = 'active'").fetchone()[0]
        total_storage = conn.execute("SELECT SUM(storage_usage) FROM camera_feeds WHERE status = 'active'").fetchone()[0]
        
        # Recent activity (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_updates = conn.execute("""
            SELECT COUNT(*) FROM camera_feeds 
            WHERE last_updated > ? AND status = 'active'
        """, (week_ago,)).fetchone()[0]
        
        conn.close()
        
        # Calculate health score
        uptime_percentage = (active_cameras / total_cameras) * 100 if total_cameras > 0 else 0
        error_percentage = (error_cameras / total_cameras) * 100 if total_cameras > 0 else 0
        
        health_score = max(0, 100 - error_percentage - (100 - uptime_percentage) * 0.5)
        
        return {
            "system_health": {
                "health_score": round(health_score, 1),
                "status": "Good" if health_score > 80 else "Fair" if health_score > 60 else "Poor"
            },
            "camera_status": {
                "total_cameras": total_cameras,
                "active_cameras": active_cameras,
                "error_cameras": error_cameras,
                "maintenance_cameras": maintenance_cameras,
                "uptime_percentage": round(uptime_percentage, 2)
            },
            "performance_metrics": {
                "average_clarity": round(avg_clarity, 2) if avg_clarity else 0,
                "total_bandwidth_mbps": round(total_bandwidth, 2) if total_bandwidth else 0,
                "total_storage_gb": round(total_storage, 2) if total_storage else 0
            },
            "recent_activity": {
                "cameras_updated_last_week": recent_updates,
                "activity_level": "High" if recent_updates > total_cameras * 0.5 else "Medium" if recent_updates > total_cameras * 0.2 else "Low"
            }
        }

# MCP Tool Functions
def get_top_cameras_by_clarity_tool(region: str = None, limit: int = 10) -> str:
    """MCP Tool: Get top cameras by clarity score"""
    tools = AnalysisTools()
    results = tools.get_top_cameras_by_clarity(region, limit)
    return json.dumps(results, indent=2)

def get_performance_analysis_tool(region: str = None) -> str:
    """MCP Tool: Get performance analysis"""
    tools = AnalysisTools()
    results = tools.get_performance_analysis(region)
    return json.dumps(results, indent=2)

def get_region_comparison_tool() -> str:
    """MCP Tool: Compare performance across regions"""
    tools = AnalysisTools()
    results = tools.get_region_comparison()
    return json.dumps(results, indent=2)

def get_encoder_decoder_analysis_tool() -> str:
    """MCP Tool: Analyze encoder/decoder usage"""
    tools = AnalysisTools()
    results = tools.get_encoder_decoder_analysis()
    return json.dumps(results, indent=2)

def get_bandwidth_optimization_suggestions_tool() -> str:
    """MCP Tool: Get bandwidth optimization suggestions"""
    tools = AnalysisTools()
    results = tools.get_bandwidth_optimization_suggestions()
    return json.dumps(results, indent=2)

def get_clarity_improvement_opportunities_tool() -> str:
    """MCP Tool: Get clarity improvement opportunities"""
    tools = AnalysisTools()
    results = tools.get_clarity_improvement_opportunities()
    return json.dumps(results, indent=2)

def get_health_status_report_tool() -> str:
    """MCP Tool: Get system health report"""
    tools = AnalysisTools()
    results = tools.get_health_status_report()
    return json.dumps(results, indent=2)
