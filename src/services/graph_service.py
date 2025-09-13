"""
Graph Service - LangGraph workflow builder
Focuses only on graph construction and edge logic
"""

import sys
import os
from typing import Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, START, END
# SqliteSaver not needed for basic graph visualization
from models.state_models import AgentState

# Import node and edge functions
from .nodes import (
    start_node,
    summarize_conversation,
    mcp_client_node,
    route_after_start
)

def build_graph() -> StateGraph:
    """Build and return the LangGraph workflow"""
    
    # Create graph builder
    graph_builder = StateGraph(AgentState)
    
    # Add all nodes
    graph_builder.add_node("start", start_node)
    graph_builder.add_node("summarize", summarize_conversation)
    graph_builder.add_node("mcp_client", mcp_client_node)
    
    # Add edges
    graph_builder.add_edge(START, "start")
    
    # Conditional edge from start node based on message count
    graph_builder.add_conditional_edges(
        "start",
        route_after_start,
        {
            "summarize": "summarize",
            "mcp_client": "mcp_client",
        }
    )
    
    # Direct edge from summarize to MCP client
    graph_builder.add_edge("summarize", "mcp_client")
    
    # End after MCP client processing
    graph_builder.add_edge("mcp_client", END)
    
    return graph_builder


def create_graph() -> Any:
    """Create and compile the graph"""
    graph_builder = build_graph()
    graph = graph_builder.compile()
    print("Graph compiled successfully")
    return graph


# Create default graph instance
graph = create_graph()
