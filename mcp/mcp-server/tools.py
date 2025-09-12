#!/usr/bin/env python3
"""
MCP Server Tools - Simple RAG Query Tool
Goal: Store chunks from data files to Qdrant as vector embeddings and query them
"""

# Standard library imports
import importlib.util
import sys
from typing import List, Dict, Any

# Local imports
from constants import RAG_NOT_INITIALIZED, RAG_QUERY_ERROR, DB_CONNECTION_ERROR, DB_QUERY_ERROR

# =============================================================================
# RAG QUERY TOOL
# =============================================================================

def rag_query_tool(query: str, top_k: int = 5) -> str:
    """
    MCP Tool: Query the RAG system for information from camera feeds and related data
    Returns: Formatted response with answer and source documents
    """
    try:
        from rag_service import get_rag_instance
        rag = get_rag_instance()
        if rag is None:
            return f"Error: {RAG_NOT_INITIALIZED}"
        
        # Update retriever k value
        rag.retriever.search_kwargs["k"] = top_k
        
        result = rag({"query": query})
        
        answer = result["result"]
        sources = result.get("source_documents", [])
        
        response = f"Answer: {answer}\n\n"
        if sources:
            response += "Sources:\n"
            for i, source in enumerate(sources, 1):
                response += f"{i}. {source.page_content}\n"
        
        return response
        
    except Exception as e:
        return f"{RAG_QUERY_ERROR}: {str(e)}"

# =============================================================================
# SQL QUERY TOOL
# =============================================================================

def sql_query_tool(query: str) -> str:
    """
    MCP Tool: Execute SQL query on camera feeds database
    Returns: Query results as formatted string
    """
    try:
        # Import database-service module (handling hyphen in filename)
        spec = importlib.util.spec_from_file_location("database_service", "database-service.py")
        database_service = importlib.util.module_from_spec(spec)
        sys.modules["database_service"] = database_service
        spec.loader.exec_module(database_service)
        
        conn = database_service.get_db_connection()
        if conn is None:
            return f"Error: {DB_CONNECTION_ERROR}"
        
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Get results
        results = cursor.fetchall()
        
        cursor.close()
        
        if not results:
            return "Query executed successfully. No results returned."
        
        # Format results
        response = f"Query Results ({len(results)} rows):\n\n"
        
        # Add column headers
        response += " | ".join(columns) + "\n"
        response += "-" * (len(" | ".join(columns))) + "\n"
        
        # Add data rows
        for row in results:
            row_values = [str(value) for value in row]
            response += " | ".join(row_values) + "\n"
        
        return response
        
    except Exception as e:
        return f"{DB_QUERY_ERROR}: {str(e)}"
