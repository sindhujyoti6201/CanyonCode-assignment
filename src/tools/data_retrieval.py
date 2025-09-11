"""
MCP Tools for Data Retrieval Operations
Provides tools for querying camera feeds, encoder/decoder parameters
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
import sqlite3
from datetime import datetime

class DataRetrievalTools:
    """MCP Tools for retrieving camera feed data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self._load_data()
        self._setup_database()
    
    def _load_data(self):
        """Load all data files"""
        # Load schemas
        with open(self.data_dir / "encoder_schema.json") as f:
            self.encoder_schema = json.load(f)
        
        with open(self.data_dir / "decoder_schema.json") as f:
            self.decoder_schema = json.load(f)
        
        with open(self.data_dir / "table_definition.json") as f:
            self.table_definition = json.load(f)
        
        # Load data
        with open(self.data_dir / "camera_feeds.json") as f:
            self.camera_feeds = json.load(f)
        
        with open(self.data_dir / "encoder_parameters.json") as f:
            self.encoder_parameters = json.load(f)
        
        with open(self.data_dir / "decoder_parameters.json") as f:
            self.decoder_parameters = json.load(f)
    
    def _setup_database(self):
        """Setup SQLite database for efficient querying"""
        self.db_path = self.data_dir / "camera_feeds.db"
        conn = sqlite3.connect(self.db_path)
        
        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS camera_feeds (
                camera_id TEXT PRIMARY KEY,
                location TEXT,
                region TEXT,
                clarity_score REAL,
                status TEXT,
                encoder_config_id TEXT,
                decoder_config_id TEXT,
                last_updated TEXT,
                bandwidth_usage REAL,
                storage_usage REAL
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS encoder_parameters (
                id TEXT PRIMARY KEY,
                bitrate INTEGER,
                resolution TEXT,
                framerate INTEGER,
                codec TEXT,
                quality_preset TEXT,
                gop_size INTEGER
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decoder_parameters (
                id TEXT PRIMARY KEY,
                buffer_size INTEGER,
                hardware_acceleration BOOLEAN,
                thread_count INTEGER,
                output_format TEXT,
                deinterlace BOOLEAN,
                color_space TEXT
            )
        """)
        
        # Insert data
        for feed in self.camera_feeds:
            conn.execute("""
                INSERT OR REPLACE INTO camera_feeds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feed["camera_id"], feed["location"], feed["region"], feed["clarity_score"],
                feed["status"], feed["encoder_config_id"], feed["decoder_config_id"],
                feed["last_updated"], feed["bandwidth_usage"], feed["storage_usage"]
            ))
        
        for enc in self.encoder_parameters:
            conn.execute("""
                INSERT OR REPLACE INTO encoder_parameters VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                enc["id"], enc["bitrate"], enc["resolution"], enc["framerate"],
                enc["codec"], enc["quality_preset"], enc["gop_size"]
            ))
        
        for dec in self.decoder_parameters:
            conn.execute("""
                INSERT OR REPLACE INTO decoder_parameters VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dec["id"], dec["buffer_size"], dec["hardware_acceleration"], dec["thread_count"],
                dec["output_format"], dec["deinterlace"], dec["color_space"]
            ))
        
        conn.commit()
        conn.close()
    
    def get_camera_feeds(self, 
                        region: Optional[str] = None,
                        status: Optional[str] = None,
                        min_clarity: Optional[float] = None,
                        max_clarity: Optional[float] = None,
                        location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve camera feeds with optional filtering
        
        Args:
            region: Filter by geographic region
            status: Filter by camera status
            min_clarity: Minimum clarity score
            max_clarity: Maximum clarity score
            location: Filter by specific location
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = "SELECT * FROM camera_feeds WHERE 1=1"
        params = []
        
        if region:
            query += " AND region = ?"
            params.append(region)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if min_clarity is not None:
            query += " AND clarity_score >= ?"
            params.append(min_clarity)
        
        if max_clarity is not None:
            query += " AND clarity_score <= ?"
            params.append(max_clarity)
        
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        
        cursor = conn.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_encoder_parameters(self, config_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get encoder parameters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        if config_id:
            cursor = conn.execute("SELECT * FROM encoder_parameters WHERE id = ?", (config_id,))
        else:
            cursor = conn.execute("SELECT * FROM encoder_parameters")
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_decoder_parameters(self, config_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get decoder parameters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        if config_id:
            cursor = conn.execute("SELECT * FROM decoder_parameters WHERE id = ?", (config_id,))
        else:
            cursor = conn.execute("SELECT * FROM decoder_parameters")
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_camera_with_configs(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Get camera feed with its encoder and decoder configurations"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT cf.*, ep.*, dp.*
            FROM camera_feeds cf
            LEFT JOIN encoder_parameters ep ON cf.encoder_config_id = ep.id
            LEFT JOIN decoder_parameters dp ON cf.decoder_config_id = dp.id
            WHERE cf.camera_id = ?
        """, (camera_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def get_regions(self) -> List[str]:
        """Get list of all regions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT DISTINCT region FROM camera_feeds ORDER BY region")
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_locations(self, region: Optional[str] = None) -> List[str]:
        """Get list of all locations, optionally filtered by region"""
        conn = sqlite3.connect(self.db_path)
        
        if region:
            cursor = conn.execute("SELECT DISTINCT location FROM camera_feeds WHERE region = ? ORDER BY location", (region,))
        else:
            cursor = conn.execute("SELECT DISTINCT location FROM camera_feeds ORDER BY location")
        
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get summary statistics about camera feeds"""
        conn = sqlite3.connect(self.db_path)
        
        # Total cameras
        total_cameras = conn.execute("SELECT COUNT(*) FROM camera_feeds").fetchone()[0]
        
        # Status distribution
        status_dist = {}
        cursor = conn.execute("SELECT status, COUNT(*) FROM camera_feeds GROUP BY status")
        for row in cursor.fetchall():
            status_dist[row[0]] = row[1]
        
        # Region distribution
        region_dist = {}
        cursor = conn.execute("SELECT region, COUNT(*) FROM camera_feeds GROUP BY region")
        for row in cursor.fetchall():
            region_dist[row[0]] = row[1]
        
        # Clarity statistics
        clarity_stats = conn.execute("""
            SELECT 
                MIN(clarity_score) as min_clarity,
                MAX(clarity_score) as max_clarity,
                AVG(clarity_score) as avg_clarity
            FROM camera_feeds
        """).fetchone()
        
        # Bandwidth and storage statistics
        usage_stats = conn.execute("""
            SELECT 
                AVG(bandwidth_usage) as avg_bandwidth,
                AVG(storage_usage) as avg_storage
            FROM camera_feeds
        """).fetchone()
        
        conn.close()
        
        return {
            "total_cameras": total_cameras,
            "status_distribution": status_dist,
            "region_distribution": region_dist,
            "clarity_statistics": {
                "min": clarity_stats[0],
                "max": clarity_stats[1],
                "average": round(clarity_stats[2], 2)
            },
            "usage_statistics": {
                "average_bandwidth_mbps": round(usage_stats[0], 2),
                "average_storage_gb": round(usage_stats[1], 2)
            }
        }
    
    def search_cameras(self, query: str) -> List[Dict[str, Any]]:
        """Search cameras by location, region, or camera_id"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        search_term = f"%{query.lower()}%"
        cursor = conn.execute("""
            SELECT * FROM camera_feeds 
            WHERE LOWER(camera_id) LIKE ? 
               OR LOWER(location) LIKE ? 
               OR LOWER(region) LIKE ?
            ORDER BY clarity_score DESC
        """, (search_term, search_term, search_term))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results

# MCP Tool Functions
def get_camera_feeds_tool(region: str = None, status: str = None, 
                         min_clarity: float = None, max_clarity: float = None,
                         location: str = None) -> str:
    """MCP Tool: Get camera feeds with filtering options"""
    tools = DataRetrievalTools()
    results = tools.get_camera_feeds(region, status, min_clarity, max_clarity, location)
    return json.dumps(results, indent=2)

def get_encoder_parameters_tool(config_id: str = None) -> str:
    """MCP Tool: Get encoder parameters"""
    tools = DataRetrievalTools()
    results = tools.get_encoder_parameters(config_id)
    return json.dumps(results, indent=2)

def get_decoder_parameters_tool(config_id: str = None) -> str:
    """MCP Tool: Get decoder parameters"""
    tools = DataRetrievalTools()
    results = tools.get_decoder_parameters(config_id)
    return json.dumps(results, indent=2)

def get_camera_with_configs_tool(camera_id: str) -> str:
    """MCP Tool: Get camera with its encoder and decoder configurations"""
    tools = DataRetrievalTools()
    result = tools.get_camera_with_configs(camera_id)
    return json.dumps(result, indent=2) if result else "Camera not found"

def get_regions_tool() -> str:
    """MCP Tool: Get list of all regions"""
    tools = DataRetrievalTools()
    results = tools.get_regions()
    return json.dumps(results, indent=2)

def get_locations_tool(region: str = None) -> str:
    """MCP Tool: Get list of locations"""
    tools = DataRetrievalTools()
    results = tools.get_locations(region)
    return json.dumps(results, indent=2)

def get_statistics_tool() -> str:
    """MCP Tool: Get summary statistics"""
    tools = DataRetrievalTools()
    results = tools.get_statistics()
    return json.dumps(results, indent=2)

def search_cameras_tool(query: str) -> str:
    """MCP Tool: Search cameras by query"""
    tools = DataRetrievalTools()
    results = tools.search_cameras(query)
    return json.dumps(results, indent=2)
