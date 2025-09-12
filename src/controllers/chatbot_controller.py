#!/usr/bin/env python3
"""
Chatbot Controller - Handles chatbot conversation endpoint using Graph Service
"""

from fastapi import APIRouter, HTTPException
from models.query_models import QueryRequest, QueryResponse
from services.graph_service import graph

router = APIRouter()

@router.post("/chat", response_model=QueryResponse)
async def send_message(request: QueryRequest):
    """Send a message to the chatbot and get response using graph workflow"""
    try:
        # Create input state for the graph
        input_state = {
            "messages": [{"role": "user", "content": request.query}]
        }
        
        # Run the graph workflow
        result = graph.invoke(input_state)
        
        # Extract the response from the last AI message
        response_text = "No response generated"
        if "messages" in result:
            for msg in reversed(result["messages"]):
                if hasattr(msg, 'content'):
                    response_text = msg.content
                    break
        
        return QueryResponse(
            response=response_text
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")
