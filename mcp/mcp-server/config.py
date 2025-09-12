#!/usr/bin/env python3
"""
MCP Server Configuration - Tool Definitions
"""

# =============================================================================
# MCP TOOL DEFINITIONS
# =============================================================================

# RAG Query Tool
RAG_TOOL = {
    "name": "rag_query_tool",
    "description": "Query the RAG system for information from camera feeds and related data",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The natural language query to search for"
            },
            "top_k": {
                "type": "integer",
                "description": "Number of top relevant documents to retrieve",
                "default": 5
            }
        },
        "required": ["query"]
    }
}

# SQL Query Tool
SQL_TOOL = {
    "name": "sql_query_tool",
    "description": "Execute SQL query on camera feeds database",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The SQL query to execute"
            }
        },
        "required": ["query"]
    }
}

# All available tools
MCP_TOOLS = [RAG_TOOL, SQL_TOOL]
