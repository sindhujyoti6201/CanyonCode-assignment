#!/usr/bin/env python3
"""
Models package - Pydantic models for the Camera Feed Query System
"""

from .query_models import QueryRequest, QueryResponse

__all__ = [
    "QueryRequest",
    "QueryResponse"
]
