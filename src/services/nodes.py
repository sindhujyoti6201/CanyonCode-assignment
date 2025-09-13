"""
Node Functions for LangGraph Workflow
Contains all node and edge logic functions used in the graph
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, RemoveMessage
from langchain_openai import ChatOpenAI
from models.state_models import AgentState
# Import MCP client to call MCP server tools
from .mcp_client import rag_query_via_mcp, sql_query_via_mcp


# Node functions
def start_node(state: AgentState) -> AgentState:
    """Start node: Process the initial query"""
    # This node just passes through the state without modification
    # The routing logic is handled by edge functions
    return state


def summarize_conversation(state: AgentState) -> AgentState:
    """Summarize the conversation and trim old messages"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    
    # Get existing summary
    summary = state.get("summary", "")
    
    # Create summarization prompt
    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"
    
    # Add prompt to history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm.invoke(messages)
    
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    
    return {"summary": response.content, "messages": delete_messages}


def mcp_client_node(state: AgentState) -> AgentState:
    """MCP Client node: ReAct-style tool selection and execution"""
    print(f"\n🚀 MCP Client Node Started")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    
    # Get the latest user message
    messages = state.get("messages", [])
    print(f"📨 Messages count: {len(messages)}")
    
    if not messages:
        print("❌ No messages found")
        return {"messages": [AIMessage(content="No message to process")]}
    
    latest_message = messages[-1]
    print(f"📝 Latest message type: {type(latest_message)}")
    
    if isinstance(latest_message, HumanMessage):
        query = latest_message.content
        print(f"❓ User query: {query}")
        
        # Step 1: Analyze the query to determine intent
        print(f"🔍 Analyzing query intent...")
        intent_analysis = analyze_query_intent(query, llm)
        print(f"🎯 Intent analysis result: {intent_analysis}")
        
        if intent_analysis["intent"] == "general_greeting":
            print("👋 Handling as general greeting")
            return {"messages": [AIMessage(content="Hello! I'm your Camera Feed Query Assistant. I can help you with questions about camera feeds, system configurations, encoding/decoding parameters, and data analysis. What would you like to know?")]}
        
        elif intent_analysis["intent"] == "metadata_query":
            print("📚 Handling as metadata query")
            # Use RAG tool for general information about schemas, parameters, etc.
            rag_response = call_rag_tool(query, llm)
            print(f"📖 RAG response: {rag_response[:100]}...")
            return {"messages": [AIMessage(content=rag_response)]}
        
        elif intent_analysis["intent"] == "data_query":
            print("📊 Handling as data query")
            # First get metadata, then formulate and execute SQL
            print("🔍 Step 1: Getting RAG context...")
            rag_response = call_rag_tool(query, llm)
            print(f"📖 RAG response: {rag_response[:100]}...")
            
            print("🔍 Step 2: Formulating SQL query...")
            sql_query = formulate_sql_query(query, rag_response, llm)
            print(f"📝 Generated SQL: {sql_query}")
            
            print("🔍 Step 3: Executing SQL query...")
            sql_result = call_sql_tool(sql_query, llm)
            print(f"📊 SQL result: {sql_result[:100]}...")
            
            print("🔍 Step 4: Generating detailed response...")
            detailed_response = generate_detailed_response(query, sql_result, llm)
            print(f"📝 Detailed response: {detailed_response[:100]}...")
            
            print(f"✅ Final response length: {len(detailed_response)}")
            return {"messages": [AIMessage(content=detailed_response)]}
        
        else:
            print(f"❓ Unknown intent: {intent_analysis['intent']}")
            return {"messages": [AIMessage(content="I'm not sure how to help with that. Please ask about camera feeds, system configurations, or data analysis.")]}
    else:
        print("❌ Latest message is not a HumanMessage")
        return {"messages": [AIMessage(content="Please provide a question to query the data")]}


def analyze_query_intent(query: str, llm: ChatOpenAI) -> dict:
    """Analyze user query to determine intent and appropriate tool"""
    intent_prompt = f"""
    Analyze this user query and determine the intent:
    
    Query: "{query}"
    
    Classify the intent as one of:
    1. "general_greeting" - ONLY simple greetings like "hi", "hello", "hey" (nothing else)
    2. "data_query" - Questions asking for specific data, lists, counts, numbers, or analysis of actual camera feed data
    3. "metadata_query" - ALL OTHER queries including questions about schemas, parameters, configurations, definitions, how things work, what something means, criteria, quality standards, technical concepts, explanations, etc.
    
    IMPORTANT RULES:
    - ONLY classify as "general_greeting" if the query is JUST a simple greeting (hi, hello, hey)
    - Questions with "how many", "which", "what cameras", "show me", "list", "count" should be classified as data_query
    - EVERYTHING ELSE that is not a simple greeting and not asking for specific data should be classified as metadata_query
    
    Examples:
    - "Hi" -> general_greeting
    - "Hello" -> general_greeting
    - "Hey" -> general_greeting
    - "What is the encoder schema?" -> metadata_query  
    - "How does H265 encoding work?" -> metadata_query
    - "What does the CODEC field mean?" -> metadata_query
    - "What is the criteria for video quality?" -> metadata_query
    - "How can we identify video quality?" -> metadata_query
    - "What determines feed quality?" -> metadata_query
    - "What are the camera IDs that are capturing the pacific area with the best clarity?" -> data_query
    - "How many cameras are in Pacific region?" -> data_query
    - "What cameras are in Pacific region?" -> data_query
    - "Show me all 4K cameras" -> data_query
    - "Count cameras by region" -> data_query
    - "Which cameras have H265 codec?" -> data_query
    - "List all cameras with high resolution" -> data_query
    
    Respond with JSON: {{"intent": "intent_type", "confidence": 0.9, "reasoning": "explanation"}}
    """
    
    response = llm.invoke([HumanMessage(content=intent_prompt)])
    
    print(f"🔍 LLM Intent Response: '{response.content}'")
    
    try:
        import json
        import re
        
        # Extract JSON from markdown code blocks if present
        content = response.content.strip()
        
        # Remove markdown code block formatting
        if content.startswith('```json'):
            content = content[7:]  # Remove ```json
        elif content.startswith('```'):
            content = content[3:]   # Remove ```
        
        if content.endswith('```'):
            content = content[:-3]  # Remove trailing ```
        
        content = content.strip()
        
        result = json.loads(content)
        print(f"✅ Parsed intent: {result}")
        return result
    except Exception as e:
        print(f"❌ Error in LLM intent analysis: {e}")
        print(f"Raw response content: '{response.content}'")
        # If LLM fails, default to metadata_query to be safe
        return {"intent": "metadata_query", "confidence": 0.5, "reasoning": f"LLM analysis failed: {str(e)}"}


def call_rag_tool(query: str, llm: ChatOpenAI) -> str:
    """Call RAG tool and return formatted response"""
    print(f"🔍 RAG Tool: Starting query: {query}")
    try:
        # Tool call to RAG
        print(f"🔍 RAG Tool: Calling rag_query_via_mcp...")
        rag_response = rag_query_via_mcp(query, top_k=5)
        print(f"🔍 RAG Tool: Raw response: {rag_response[:200]}...")
        
        # Format the response
        if "Error:" in rag_response:
            print(f"❌ RAG Tool: Error in response")
            return f"RAG Query Error: {rag_response}"
        else:
            # Remove sources section from response
            print(f"🔍 RAG Tool: Removing sources...")
            cleaned_response = remove_sources_from_response(rag_response)
            print(f"🔍 RAG Tool: After removing sources: {cleaned_response[:200]}...")
            
            # Clean up markdown formatting
            print(f"🔍 RAG Tool: Cleaning markdown...")
            styled_response = clean_markdown_formatting(cleaned_response)
            print(f"🔍 RAG Tool: Final styled response: {styled_response[:200]}...")
            return styled_response
    except Exception as e:
        print(f"❌ RAG Tool: Exception: {str(e)}")
        return f"RAG Tool Error: {str(e)}"


def formulate_sql_query(query: str, rag_context: str, llm: ChatOpenAI) -> str:
    """Formulate SQL query based on user query and RAG context"""
    sql_prompt = f"""
    Based on the user query: "{query}"
    And the relevant metadata information: "{rag_context}"
    
    Generate a SQL query to answer the user's question.
    Use the metadata to understand the table structure and relationships.
    docker-compose down && docker-compose up --build -d
    The name of the table is "camera_feeds".
    Important: Return ONLY the SQL query, no markdown formatting, no explanations, no backticks.
    Just the pure SQL statement.
    
    Example table structure from the data:
    - feed_id: Camera identifier
    - theater: Region (PAC, EUR, CONUS, ME, AFR, ARC)
    - frrate: Frame rate
    - res_w, res_h: Resolution width and height
    - codec: Video codec (H264, H265, VP9, MPEG2, AV1)
    - encr: Encryption status
    - lat_ms: Latency in milliseconds
    - modl_tag: Model tag
    - civ_ok: Civilian status
    
    For counting questions (like "how many cameras"), use COUNT(*) with appropriate WHERE clauses.
    For listing questions, use SELECT * with appropriate WHERE clauses.
    """
    
    response = llm.invoke([HumanMessage(content=sql_prompt)])
    sql_query = response.content.strip()
    
    # Clean up any markdown formatting
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:]
    if sql_query.startswith("```"):
        sql_query = sql_query[3:]
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3]
    
    sql_query = sql_query.strip()
    
    # Print/log the generated SQL query
    print(f"\n🔍 Generated SQL Query:")
    print(f"📝 Query: {sql_query}")
    print(f"📊 User Question: {query}")
    print("-" * 80)
    
    return sql_query


def call_sql_tool(sql_query: str, llm: ChatOpenAI) -> str:
    """Call SQL tool and return formatted response"""
    print(f"🔍 SQL Tool: Starting query: {sql_query}")
    try:
        # Print/log the SQL query being executed
        print(f"\n⚡ Executing SQL Query:")
        print(f"🔧 Query: {sql_query}")
        print("-" * 80)
        
        # Tool call to SQL
        print(f"🔍 SQL Tool: Calling sql_query_via_mcp...")
        sql_result = sql_query_via_mcp(sql_query)
        print(f"🔍 SQL Tool: Raw SQL result: {sql_result[:200]}...")
        
        # Print/log the SQL result
        print(f"\n📋 SQL Query Result:")
        print(f"✅ Result: {sql_result[:200]}{'...' if len(sql_result) > 200 else ''}")
        print("-" * 80)
        
        # Format the response
        if "Error:" in sql_result:
            print(f"❌ SQL Tool: Error in result")
            return f"SQL Query Error: {sql_result}"
        else:
            # Clean up the SQL result formatting
            print(f"🔍 SQL Tool: Cleaning result formatting...")
            cleaned_result = clean_sql_result_formatting(sql_result)
            print(f"🔍 SQL Tool: Final cleaned result: {cleaned_result[:200]}...")
            return cleaned_result
    except Exception as e:
        print(f"\n❌ SQL Tool Error: {str(e)}")
        print("-" * 80)
        return f"SQL Tool Error: {str(e)}"


def remove_sources_from_response(response: str) -> str:
    """Remove sources section from RAG response"""
    # Split by "Sources:" and take only the first part
    if "Sources:" in response:
        return response.split("Sources:")[0].strip()
    return response


def clean_markdown_formatting(response: str) -> str:
    """Clean up markdown formatting for better readability"""
    import re
    
    # Remove "Answer:" prefix if present
    if response.startswith("Answer:"):
        response = response[7:].strip()
    
    # Remove "RAG Analysis Results:" prefix if present
    if "RAG Analysis Results:" in response:
        response = response.replace("RAG Analysis Results:", "").strip()
    
    # Clean up excessive markdown formatting
    # Replace **text** with just text (remove bold formatting)
    response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
    
    # Replace *text* with just text (remove italic formatting)
    response = re.sub(r'\*(.*?)\*', r'\1', response)
    
    # Clean up bullet points - replace - with •
    response = re.sub(r'^- ', '• ', response, flags=re.MULTILINE)
    
    # Remove excessive line breaks (more than 2 consecutive)
    response = re.sub(r'\n{3,}', '\n\n', response)
    
    # Clean up any remaining markdown artifacts
    response = response.replace('```', '').replace('`', '')
    
    return response.strip()


def clean_sql_result_formatting(sql_result: str) -> str:
    """Clean up SQL result formatting for better readability"""
    import re
    
    # Remove "SQL Results:" prefix if present
    if sql_result.startswith("SQL Results:"):
        sql_result = sql_result[12:].strip()
    
    # Remove "Query Results (X rows):" prefix if present
    sql_result = re.sub(r'^Query Results \(\d+ rows\):\s*\n', '', sql_result)
    
    # Remove table separators (lines with dashes)
    sql_result = re.sub(r'^-+\s*$', '', sql_result, flags=re.MULTILINE)
    
    # Clean up excessive line breaks
    sql_result = re.sub(r'\n{3,}', '\n\n', sql_result)
    
    # Remove empty lines at the beginning and end
    sql_result = sql_result.strip()
    
    return sql_result


def generate_detailed_response(query: str, sql_result: str, llm: ChatOpenAI) -> str:
    """Generate a detailed, user-friendly response based on the query and SQL results"""
    response_prompt = f"""
    Based on the user's question and the SQL query results, provide a detailed, conversational response.
    
    User Question: "{query}"
    SQL Results: "{sql_result}"
    
    Instructions:
    1. Provide a clear, direct answer to the user's question
    2. Make the response conversational and easy to understand
    3. Include relevant details from the data
    4. If it's a counting question, provide context about what the number represents
    5. If it's a listing question, summarize the key findings
    6. Keep the response concise but informative
    7. Don't mention SQL queries or technical details
    
    Examples:
    - For "How many cameras are in Pacific region?" with result "26" -> "There are 26 cameras in the Pacific region."
    - For "What cameras are in Pacific region?" with a list -> "Here are the cameras in the Pacific region: [list with details]"
    
    Provide only the response, no additional formatting or explanations.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=response_prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"❌ Error generating detailed response: {str(e)}")
        # Fallback to cleaned SQL result
        return clean_sql_result_formatting(sql_result)


# Edge functions
def route_after_start(state: AgentState) -> str:
    """Route after start node based on message count"""
    messages = state.get("messages", [])
    
    # If more than 5 messages, we need to summarize first
    if len(messages) > 5:
        return "summarize"
    else:
        return "mcp_client"


