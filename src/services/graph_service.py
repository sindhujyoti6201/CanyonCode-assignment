"""
Graph Service - LangGraph workflow builder
Focuses only on graph construction and edge logic
"""

import sys
import os
from typing import Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, START, END
from models.state_models import AgentState
from typing import Dict, List
import threading
from datetime import datetime

# Import node and edge functions
from .nodes import (
    start_node,
    summarize_conversation,
    mcp_client_node,
    route_after_start
)

# In-memory conversation storage
conversation_memory: Dict[str, List[Dict[str, str]]] = {}
memory_lock = threading.Lock()

def get_conversation_history(thread_id: str, limit: int = 20) -> List:
    """Get conversation history for a thread from in-memory storage"""
    with memory_lock:
        if thread_id not in conversation_memory:
            return []
        
        # Get the last 'limit' messages
        history = conversation_memory[thread_id][-limit:] if len(conversation_memory[thread_id]) > limit else conversation_memory[thread_id]
        
        # Convert to LangChain messages
        from langchain_core.messages import HumanMessage, AIMessage
        messages = []
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        return messages

def save_message(thread_id: str, role: str, content: str):
    """Save a message to the in-memory conversation history"""
    with memory_lock:
        if thread_id not in conversation_memory:
            conversation_memory[thread_id] = []
        
        conversation_memory[thread_id].append({
            "role": role,
            "content": content,
            "timestamp": str(datetime.now())
        })
        
        # Keep only the last 50 messages per thread to prevent memory bloat
        if len(conversation_memory[thread_id]) > 50:
            conversation_memory[thread_id] = conversation_memory[thread_id][-50:]

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


class GraphWithMemory:
    """Graph wrapper with in-memory conversation memory"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def invoke(self, input_state, config=None):
        """Invoke the graph with memory management"""
        # Extract thread_id from config
        thread_id = "default"
        if config and "configurable" in config and "thread_id" in config["configurable"]:
            thread_id = config["configurable"]["thread_id"]
        
        # Get conversation history
        history = get_conversation_history(thread_id)
        
        # Save the current user message to memory first
        if "messages" in input_state and input_state["messages"]:
            for msg in input_state["messages"]:
                if hasattr(msg, 'content') and hasattr(msg, '__class__') and 'Human' in msg.__class__.__name__:
                    save_message(thread_id, "user", msg.content)
        
        # Merge history with current messages
        if "messages" in input_state:
            # Combine history with new messages
            all_messages = history + input_state["messages"]
            input_state["messages"] = all_messages
        
        # Run the graph
        result = self.graph.invoke(input_state)
        
        # Save the AI response to memory
        if "messages" in result:
            for msg in result["messages"]:
                if hasattr(msg, 'content') and hasattr(msg, '__class__') and 'AI' in msg.__class__.__name__:
                    save_message(thread_id, "assistant", msg.content)
                    break  # Only save the first AI response
        
        return result

def create_graph() -> Any:
    """Create and compile the graph with in-memory state management"""
    # Build and compile the graph
    graph_builder = build_graph()
    compiled_graph = graph_builder.compile()
    
    # Wrap with memory management
    graph_with_memory = GraphWithMemory(compiled_graph)
    print("Graph compiled successfully with in-memory state management")
    return graph_with_memory


# Create default graph instance
graph = create_graph()
