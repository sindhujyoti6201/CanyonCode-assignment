# Agentic Query System - Camera Feed Analysis

An intelligent agentic query system for analyzing camera feeds, encoders, and decoders using LangGraph, MCP (Model Context Protocol), and React TypeScript frontend.

## 🎯 Project Overview

This system provides natural language querying capabilities for camera feed data, designed for BS/MS/PhD students with ML research backgrounds. It demonstrates cutting-edge AI tools, agentic workflows, and modern web development practices.

## 🏗️ Architecture

![Architecture Diagram](architecture.png)

### Core Components

- **Frontend**: React TypeScript application with Material-UI
- **Backend**: FastAPI with LangGraph agentic workflow
- **MCP Server**: Model Context Protocol server with RAG and SQL tools
- **Database**: PostgreSQL with camera feed data
- **Memory**: In-memory conversation persistence

## 🚀 How to Run the Tool?

```bash
# 1. Run from ROOT directory
docker-compose up -d

# 2. Run from mcp/mcp-server directory  
docker-compose up -d

# 3. Run from frontend directory
npm start
```

## 🔧 Environment Configuration

Create `.env` file in the root directory:

```bash
# OpenAI API Key (required for LLM functionality)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# MCP Server Configuration
MCP_SERVER_URL=http://host.docker.internal:8000
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **MCP Server**: http://localhost:8000
- **Health Check**: http://localhost:8001/health


## 🤖 LangGraph Workflow

The system uses LangGraph for agentic workflow orchestration:

1. **Start Node**: Receives user query and checks message count
2. **Conditional Routing**: Routes based on conversation length
3. **Summarize Node**: Summarizes long conversations (>5 messages)
4. **MCP Client Node**: Processes queries using MCP tools
   - **RAG Tool**: Retrieves relevant metadata
   - **SQL Tool**: Executes database queries
5. **Memory Management**: Maintains conversation history

### Workflow Visualization

Generate the workflow diagram:

```bash
source venv/bin/activate
python3 src/visualization/graph_visualizer.py
```

## 🛠️ MCP Tools

### RAG Query Tool
- Retrieves relevant information about camera feeds, encoders, and decoders
- Uses vector similarity search for context-aware responses
- Provides metadata for SQL query formation

### SQL Query Tool
- Executes SQL queries against PostgreSQL database
- Supports complex queries with joins and aggregations
- Returns formatted results for LLM consumption

## 💬 Chatbot Features

### Conversation Management
- **Thread-based conversations**: Each conversation has a unique thread ID
- **In-memory persistence**: Conversation history maintained across requests
- **Context awareness**: LLM has access to previous conversation context


### Testing

```bash
# Test backend API
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the available regions?", "thread_id": "test"}'

# Test MCP server
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "rag_query_tool", "arguments": {"query": "test query"}}'
```

## 📊 API Documentation

### Chat Endpoint
- **POST** `/api/v1/chat`
- **Request**: `{"query": "string", "thread_id": "string"}`
- **Response**: `{"response": "string", "thread_id": "string"}`

### Health Check
- **GET** `/health`
- **Response**: `{"status": "healthy", "timestamp": "ISO_datetime"}`


