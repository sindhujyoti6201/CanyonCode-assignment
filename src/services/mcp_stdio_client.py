#!/usr/bin/env python3
"""
MCP Stdio Client - Direct communication with MCP server via stdio
"""

import subprocess
import json
import os
from typing import Dict, Any, Optional

class MCPStdioClient:
    """Client to communicate with MCP server via stdio"""
    
    def __init__(self, server_path: str = "../mcp/mcp-server/server.py"):
        self.server_path = server_path
        self.process = None
    
    def start_server(self):
        """Start the MCP server process"""
        if self.process is None:
            self.process = subprocess.Popen(
                ["python", self.server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
    
    def stop_server(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
    
    def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server"""
        if self.process is None:
            self.start_server()
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            # Send request
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            return {"error": f"Communication error: {str(e)}"}
    
    def rag_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Query the RAG system via MCP server"""
        return self.send_request("tools/call", {
            "name": "rag_query_tool",
            "arguments": {
                "query": query,
                "top_k": top_k
            }
        })

# Global client instance
_stdio_client = None

def get_stdio_client() -> MCPStdioClient:
    """Get or create stdio client instance"""
    global _stdio_client
    if _stdio_client is None:
        _stdio_client = MCPStdioClient()
    return _stdio_client

def rag_query_via_stdio(query: str, top_k: int = 5) -> str:
    """
    Query RAG system via MCP stdio client
    
    Args:
        query: The natural language query
        top_k: Number of documents to retrieve
        
    Returns:
        Formatted response string
    """
    client = get_stdio_client()
    result = client.rag_query(query, top_k)
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    # Extract answer from MCP response
    answer = result.get("result", {}).get("content", "No answer found")
    return answer
