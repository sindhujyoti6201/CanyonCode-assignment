#!/usr/bin/env python3
"""
Query-related Pydantic models
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    thread_id: Optional[str] = "default"

class QueryResponse(BaseModel):
    response: str
    thread_id: str
