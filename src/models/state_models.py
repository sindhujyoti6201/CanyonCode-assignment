#!/usr/bin/env python3
"""
State models for LangGraph workflows
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """Unified state for query processing and chatbot conversations"""
    messages: Annotated[List[BaseMessage], add_messages]
    tool_results: Dict[str, Any]
    summary: str  # For conversation memory and summarization
