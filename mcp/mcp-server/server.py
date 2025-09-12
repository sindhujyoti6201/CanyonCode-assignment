#!/usr/bin/env python3
"""
MCP Server for RAG Query Tool and SQL Query Tool
Hybrid MCP Server: Supports both stdio and HTTP transport
"""

import asyncio
import json
import sys
import os
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ToolsCapability,
    LoggingCapability,
    SamplingCapability,
)

# HTTP server imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import importlib.util
import sys

from tools import rag_query_tool, sql_query_tool

# Import database-service module (handling hyphen in filename)
spec = importlib.util.spec_from_file_location("database_service", "database-service.py")
database_service = importlib.util.module_from_spec(spec)
sys.modules["database_service"] = database_service
spec.loader.exec_module(database_service)

from config import MCP_TOOLS
from constants import SERVER_NAME, SERVER_VERSION

# Create the MCP server instance
mcp_server = Server(SERVER_NAME)

# HTTP Server for web clients
app = FastAPI(
    title=SERVER_NAME,
    version=SERVER_VERSION,
    description="MCP Server for RAG Query Tool and SQL Query Tool"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP Request/Response models
class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ToolCallResponse(BaseModel):
    result: str
    success: bool
    error: str = None

class ToolInfo(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

# MCP Server handlers
@mcp_server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools - MCP compliant"""
    return [
        Tool(
            name=tool["name"],
            description=tool["description"],
            inputSchema=tool["inputSchema"]
        )
        for tool in MCP_TOOLS
    ]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls - MCP compliant"""
    if name == "rag_query_tool":
        query = arguments.get("query", "")
        top_k = arguments.get("top_k", 5)
        
        result = rag_query_tool(query, top_k)
        return [TextContent(type="text", text=result)]
    
    elif name == "sql_query_tool":
        query = arguments.get("query", "")
        
        result = sql_query_tool(query)
        return [TextContent(type="text", text=result)]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

# HTTP Server endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "status": "healthy",
        "tools": len(MCP_TOOLS),
        "transport": "HTTP + MCP Stdio"
    }

@app.get("/tools", response_model=List[ToolInfo])
async def list_tools():
    """List available tools via HTTP"""
    return [
        ToolInfo(
            name=tool["name"],
            description=tool["description"],
            inputSchema=tool["inputSchema"]
        )
        for tool in MCP_TOOLS
    ]

@app.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """Call a tool with given arguments via HTTP"""
    try:
        if request.name == "rag_query_tool":
            query = request.arguments.get("query", "")
            top_k = request.arguments.get("top_k", 5)
            result = rag_query_tool(query, top_k)
            return ToolCallResponse(result=result, success=True)
        
        elif request.name == "sql_query_tool":
            query = request.arguments.get("query", "")
            result = sql_query_tool(query)
            return ToolCallResponse(result=result, success=True)
        
        else:
            return ToolCallResponse(
                result="",
                success=False,
                error=f"Unknown tool: {request.name}"
            )
    
    except Exception as e:
        return ToolCallResponse(
            result="",
            success=False,
            error=str(e)
        )

async def run_mcp_stdio():
    """Run MCP server with stdio transport"""
    print("Starting MCP server with stdio transport...")
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities={
                    "tools": ToolsCapability(listChanged=False),
                    "logging": LoggingCapability(),
                    "sampling": SamplingCapability(),
                },
            ),
        )

async def run_http_server():
    """Run HTTP server"""
    print("Starting HTTP server on port 8000...")
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Main server function - supports both transports"""
    # Initialize database (preload)
    print("Initializing database...")
    database_service.initialize_database()
    print("MCP Server ready!")
    
    # Check transport mode from environment
    transport_mode = os.getenv("TRANSPORT_MODE", "hybrid")
    print(f"Transport mode: {transport_mode}")
    
    if transport_mode == "http":
        # Run HTTP server only
        await run_http_server()
    elif transport_mode == "stdio":
        # Run MCP stdio server only
        await run_mcp_stdio()
    else:
        # Run both servers concurrently (hybrid mode)
        print("Starting both HTTP and MCP stdio servers...")
        await asyncio.gather(
            run_http_server(),
            run_mcp_stdio()
        )

if __name__ == "__main__":
    asyncio.run(main())
