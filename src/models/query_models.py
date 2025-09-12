#!/usr/bin/env python3
"""
Query-related Pydantic models
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
