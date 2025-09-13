#!/usr/bin/env python3
"""
Chatbot Controller - Handles chatbot conversation endpoint using Graph Service
"""

from fastapi import APIRouter, HTTPException
from src.models.query_models import QueryRequest, QueryResponse
from src.services.graph_service import graph
from langchain_core.messages import HumanMessage

router = APIRouter()

@router.post("/chat", response_model=QueryResponse)
async def send_message(request: QueryRequest):
    """Send a message to the chatbot and get response using graph workflow with built-in memory"""
    try:
        # Get thread_id from request, default to "default"
        thread_id = request.thread_id or "default"
        
        # Create input state for the graph
        input_state = {
            "messages": [HumanMessage(content=request.query)]
        }
        
        # Run the graph workflow with memory (thread_id passed via config)
        config = {"configurable": {"thread_id": thread_id}}
        result = graph.invoke(input_state, config=config)
        
        # Extract the response from the last AI message
        response_text = "No response generated"
        if "messages" in result:
            for msg in reversed(result["messages"]):
                if hasattr(msg, 'content'):
                    response_text = msg.content
                    break
        
        return QueryResponse(
            response=response_text,
            thread_id=thread_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")
