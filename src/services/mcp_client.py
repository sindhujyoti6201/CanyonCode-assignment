#!/usr/bin/env python3
"""
MCP Client - HTTP client to communicate with MCP RAG Query Server
"""

import requests
import json
from typing import Dict, Any, Optional

class MCPClient:
    """Client to communicate with MCP RAG Query Server"""
    
    def __init__(self, base_url: str = "http://host.docker.internal:8000"):
        self.base_url = base_url.rstrip('/')
    
    def rag_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Query the RAG system via MCP server
        
        Args:
            query: The natural language query
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with answer and source documents
        """
        try:
            # Call the MCP server HTTP API
            payload = {
                "name": "rag_query_tool",
                "arguments": {
                    "query": query,
                    "top_k": top_k
                }
            }
            
            response = requests.post(
                f"{self.base_url}/tools/call",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def sql_query(self, query: str) -> Dict[str, Any]:
        """
        Execute SQL query via MCP server
        
        Args:
            query: The SQL query to execute
            
        Returns:
            Dictionary with query results
        """
        try:
            payload = {
                "name": "sql_query_tool",
                "arguments": {
                    "query": query
                }
            }
            
            response = requests.post(
                f"{self.base_url}/tools/call",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

# Global client instance
_mcp_client = None

def get_mcp_client(base_url: str = "http://host.docker.internal:8000") -> MCPClient:
    """Get or create MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient(base_url)
    return _mcp_client

def rag_query_via_mcp(query: str, top_k: int = 5) -> str:
    """
    Query RAG system via MCP server (wrapper function)
    
    Args:
        query: The natural language query
        top_k: Number of documents to retrieve
        
    Returns:
        Formatted response string
    """
    client = get_mcp_client()
    result = client.rag_query(query, top_k)
    
    if "error" in result and result["error"] is not None:
        return f"Error: {result['error']}"
    
    # Extract answer from MCP response
    answer = result.get("result", "No answer found")
    return answer

def sql_query_via_mcp(query: str) -> str:
    """
    Execute SQL query via MCP server (wrapper function)
    
    Args:
        query: The SQL query to execute
        
    Returns:
        Formatted response string
    """
    client = get_mcp_client()
    result = client.sql_query(query)
    
    if "error" in result and result["error"] is not None:
        return f"Error: {result['error']}"
    
    # Extract results from MCP response
    answer = result.get("result", "No results found")
    return answer
