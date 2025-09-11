"""
Query Agent Service for Natural Language Query Processing
Handles camera feed queries using agentic workflow orchestration
"""

import json
import re
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# Import MCP tools
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.tools.data_retrieval import (
    get_camera_feeds_tool, get_encoder_parameters_tool, get_decoder_parameters_tool,
    get_camera_with_configs_tool, get_regions_tool, get_locations_tool,
    get_statistics_tool, search_cameras_tool
)
from src.tools.analysis_tools import (
    get_top_cameras_by_clarity_tool, get_performance_analysis_tool,
    get_region_comparison_tool, get_encoder_decoder_analysis_tool,
    get_bandwidth_optimization_suggestions_tool, get_clarity_improvement_opportunities_tool,
    get_health_status_report_tool
)

load_dotenv()

class AgentState(TypedDict):
    """State for the query processing agent"""
    messages: Annotated[List[BaseMessage], add_messages]
    query: str
    query_type: str
    extracted_params: Dict[str, Any]
    tool_results: Dict[str, Any]
    final_response: str
    error: Optional[str]

class QueryAgentService:
    """Query agent service for processing camera feed queries"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Define the workflow
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("extract_parameters", self._extract_parameters)
        workflow.add_node("execute_tools", self._execute_tools)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("handle_error", self._handle_error)
        
        # Add edges
        workflow.set_entry_point("classify_query")
        
        workflow.add_conditional_edges(
            "classify_query",
            self._should_extract_params,
            {
                "extract": "extract_parameters",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("extract_parameters", "execute_tools")
        workflow.add_edge("execute_tools", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("handle_error", END)
        
        return workflow
    
    def _classify_query(self, state: AgentState) -> AgentState:
        """Classify the type of query and determine if it's valid"""
        query = state["query"]
        
        classification_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            You are a query classifier for a camera feed analysis system. 
            Classify the user's query into one of these categories:
            
            1. "camera_search" - Finding specific cameras (by location, region, clarity, etc.)
            2. "performance_analysis" - Analyzing performance metrics, statistics
            3. "configuration_info" - Getting encoder/decoder configuration details
            4. "optimization" - Suggestions for improvements, optimizations
            5. "health_status" - System health, status reports
            6. "comparison" - Comparing regions, configurations, etc.
            7. "invalid" - Not related to camera feeds or unclear
            
            Respond with just the category name and a brief reason.
            """),
            HumanMessage(content=f"Classify this query: {query}")
        ])
        
        try:
            response = self.llm.invoke(classification_prompt.format_messages(query=query))
            classification = response.content.strip()
            
            if "invalid" in classification.lower():
                state["error"] = "Query is not related to camera feed analysis"
                state["query_type"] = "invalid"
            else:
                # Extract the main category
                if "camera_search" in classification.lower():
                    state["query_type"] = "camera_search"
                elif "performance" in classification.lower():
                    state["query_type"] = "performance_analysis"
                elif "configuration" in classification.lower():
                    state["query_type"] = "configuration_info"
                elif "optimization" in classification.lower():
                    state["query_type"] = "optimization"
                elif "health" in classification.lower():
                    state["query_type"] = "health_status"
                elif "comparison" in classification.lower():
                    state["query_type"] = "comparison"
                else:
                    state["query_type"] = "camera_search"  # Default fallback
            
        except Exception as e:
            state["error"] = f"Error classifying query: {str(e)}"
            state["query_type"] = "invalid"
        
        return state
    
    def _should_extract_params(self, state: AgentState) -> str:
        """Determine if we should extract parameters or handle error"""
        if state.get("error"):
            return "error"
        return "extract"
    
    def _extract_parameters(self, state: AgentState) -> AgentState:
        """Extract relevant parameters from the query"""
        query = state["query"]
        query_type = state["query_type"]
        
        extraction_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""
            Extract relevant parameters from the user query for a {query_type} request.
            
            For camera_search queries, extract:
            - region (Pacific, Atlantic, Gulf, Great Lakes)
            - location (specific city/harbor names)
            - min_clarity, max_clarity (clarity score ranges)
            - status (active, inactive, maintenance, error)
            - search_term (general search terms)
            
            For performance_analysis queries, extract:
            - region (if specified)
            - metric_type (clarity, bandwidth, storage, etc.)
            
            For configuration_info queries, extract:
            - config_id (specific encoder/decoder config IDs)
            - config_type (encoder, decoder, or both)
            
            For optimization queries, extract:
            - optimization_type (bandwidth, clarity, performance)
            
            For comparison queries, extract:
            - comparison_type (regions, configurations, etc.)
            - entities_to_compare (specific regions or configs)
            
            Return a JSON object with the extracted parameters. Use null for unspecified values.
            """),
            HumanMessage(content=f"Extract parameters from: {query}")
        ])
        
        try:
            response = self.llm.invoke(extraction_prompt.format_messages(query=query))
            params_text = response.content.strip()
            
            # Try to parse JSON from the response
            if "```json" in params_text:
                params_text = params_text.split("```json")[1].split("```")[0]
            elif "```" in params_text:
                params_text = params_text.split("```")[1].split("```")[0]
            
            # Clean up the JSON
            params_text = params_text.strip()
            if not params_text.startswith("{"):
                # Try to find JSON in the text
                start = params_text.find("{")
                end = params_text.rfind("}") + 1
                if start != -1 and end > start:
                    params_text = params_text[start:end]
            
            extracted_params = json.loads(params_text)
            state["extracted_params"] = extracted_params
            
        except Exception as e:
            # Fallback: try to extract basic parameters using regex
            extracted_params = self._extract_params_fallback(query)
            state["extracted_params"] = extracted_params
        
        return state
    
    def _extract_params_fallback(self, query: str) -> Dict[str, Any]:
        """Fallback parameter extraction using regex patterns"""
        params = {}
        query_lower = query.lower()
        
        # Extract region
        regions = ["pacific", "atlantic", "gulf", "great lakes"]
        for region in regions:
            if region in query_lower:
                params["region"] = region.title()
                break
        
        # Extract clarity mentions
        if "best clarity" in query_lower or "highest clarity" in query_lower:
            params["min_clarity"] = 80
        elif "good clarity" in query_lower:
            params["min_clarity"] = 70
        elif "poor clarity" in query_lower or "low clarity" in query_lower:
            params["max_clarity"] = 60
        
        # Extract status
        if "active" in query_lower:
            params["status"] = "active"
        elif "inactive" in query_lower:
            params["status"] = "inactive"
        
        return params
    
    def _execute_tools(self, state: AgentState) -> AgentState:
        """Execute the appropriate MCP tools based on query type and parameters"""
        query_type = state["query_type"]
        params = state["extracted_params"]
        tool_results = {}
        
        try:
            if query_type == "camera_search":
                # Use camera search tools
                if params.get("search_term"):
                    tool_results["search"] = search_cameras_tool(params["search_term"])
                else:
                    tool_results["cameras"] = get_camera_feeds_tool(
                        region=params.get("region"),
                        status=params.get("status"),
                        min_clarity=params.get("min_clarity"),
                        max_clarity=params.get("max_clarity"),
                        location=params.get("location")
                    )
                
                # If looking for best clarity, also get top cameras
                if params.get("min_clarity", 0) >= 80 or "best" in state["query"].lower():
                    tool_results["top_cameras"] = get_top_cameras_by_clarity_tool(
                        region=params.get("region"), limit=10
                    )
            
            elif query_type == "performance_analysis":
                tool_results["performance"] = get_performance_analysis_tool(
                    region=params.get("region")
                )
                tool_results["statistics"] = get_statistics_tool()
            
            elif query_type == "configuration_info":
                if params.get("config_type") == "encoder" or not params.get("config_type"):
                    tool_results["encoder_configs"] = get_encoder_parameters_tool(
                        config_id=params.get("config_id")
                    )
                if params.get("config_type") == "decoder" or not params.get("config_type"):
                    tool_results["decoder_configs"] = get_decoder_parameters_tool(
                        config_id=params.get("config_id")
                    )
            
            elif query_type == "optimization":
                if params.get("optimization_type") == "bandwidth":
                    tool_results["bandwidth_suggestions"] = get_bandwidth_optimization_suggestions_tool()
                elif params.get("optimization_type") == "clarity":
                    tool_results["clarity_opportunities"] = get_clarity_improvement_opportunities_tool()
                else:
                    # Get both types of suggestions
                    tool_results["bandwidth_suggestions"] = get_bandwidth_optimization_suggestions_tool()
                    tool_results["clarity_opportunities"] = get_clarity_improvement_opportunities_tool()
            
            elif query_type == "health_status":
                tool_results["health_report"] = get_health_status_report_tool()
                tool_results["statistics"] = get_statistics_tool()
            
            elif query_type == "comparison":
                tool_results["region_comparison"] = get_region_comparison_tool()
                tool_results["config_analysis"] = get_encoder_decoder_analysis_tool()
            
            state["tool_results"] = tool_results
            
        except Exception as e:
            state["error"] = f"Error executing tools: {str(e)}"
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate a natural language response based on tool results"""
        query = state["query"]
        query_type = state["query_type"]
        tool_results = state["tool_results"]
        
        response_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            You are a helpful assistant for a camera feed analysis system. 
            Generate a clear, informative response based on the query and tool results.
            
            Guidelines:
            - Be conversational and helpful
            - Provide specific data and numbers when available
            - Explain technical terms in simple language
            - If multiple cameras are found, highlight the most relevant ones
            - Include actionable insights when appropriate
            - Keep responses concise but comprehensive
            """),
            HumanMessage(content=f"""
            User Query: {query}
            Query Type: {query_type}
            Tool Results: {json.dumps(tool_results, indent=2)}
            
            Generate a helpful response to the user's query.
            """)
        ])
        
        try:
            response = self.llm.invoke(response_prompt.format_messages(
                query=query, query_type=query_type, tool_results=json.dumps(tool_results, indent=2)
            ))
            state["final_response"] = response.content.strip()
        except Exception as e:
            state["error"] = f"Error generating response: {str(e)}"
        
        return state
    
    def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors and provide helpful error messages"""
        error = state.get("error", "Unknown error occurred")
        
        error_responses = {
            "invalid": "I can help you with questions about camera feeds, their configurations, performance analysis, and system health. Could you please rephrase your question to be more specific about what you'd like to know?",
            "classification": "I'm having trouble understanding your question. Could you please ask about camera feeds, their locations, performance, or configurations?",
            "tools": "I encountered an issue while retrieving the data. Please try again or rephrase your question.",
            "response": "I found the information but had trouble formatting the response. Let me try a simpler approach."
        }
        
        # Determine error type and provide appropriate response
        if "not related" in error.lower():
            state["final_response"] = error_responses["invalid"]
        elif "classifying" in error.lower():
            state["final_response"] = error_responses["classification"]
        elif "executing tools" in error.lower():
            state["final_response"] = error_responses["tools"]
        elif "generating response" in error.lower():
            state["final_response"] = error_responses["response"]
        else:
            state["final_response"] = f"I apologize, but I encountered an issue: {error}. Please try rephrasing your question."
        
        return state
    
    def process_query(self, query: str) -> str:
        """Process a natural language query and return the response"""
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "query": query,
            "query_type": "",
            "extracted_params": {},
            "tool_results": {},
            "final_response": "",
            "error": None
        }
        
        try:
            final_state = self.app.invoke(initial_state)
            return final_state["final_response"]
        except Exception as e:
            return f"I apologize, but I encountered an error processing your query: {str(e)}. Please try again."

