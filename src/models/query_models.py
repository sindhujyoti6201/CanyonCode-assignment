#!/usr/bin/env python3
"""
Query-related Pydantic models
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    include_metadata: Optional[bool] = False

class QueryResponse(BaseModel):
    response: str
    query_type: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
