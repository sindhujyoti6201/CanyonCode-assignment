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

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.13+ (for local development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd CanyonCode-assignment
```

### 2. Environment Configuration

Create `.env` file in the root directory:

```bash
# OpenAI API Key (required for LLM functionality)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# MCP Server Configuration
MCP_SERVER_URL=http://host.docker.internal:8000
```

### 3. Start the System

```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individual services
docker-compose up -d mcp-server  # MCP Server
docker-compose up -d backend     # FastAPI Backend
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **MCP Server**: http://localhost:8000
- **Health Check**: http://localhost:8001/health

## 📁 Project Structure

```
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── types/           # TypeScript definitions
│   └── package.json
├── src/                     # FastAPI backend
│   ├── controllers/         # API controllers
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic
│   │   ├── graph_service.py    # LangGraph workflow
│   │   ├── nodes.py            # Graph nodes
│   │   └── mcp_client.py       # MCP client
│   └── application.py      # FastAPI app
├── mcp/mcp-server/         # MCP server
│   ├── server.py           # MCP server implementation
│   ├── tools.py            # Tool definitions
│   └── database-service.py # Database operations
├── data/                   # Sample data files
├── docker-compose.yml      # Docker orchestration
└── Dockerfile             # Backend container
```

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


## 🔧 Development

### Local Development Setup

1. **Backend Development**:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
cd src
python application.py
```

2. **Frontend Development**:
```bash
cd frontend
npm install
npm start
```

3. **MCP Server Development**:
```bash
cd mcp/mcp-server
pip install -r requirements.txt
python server.py
```

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

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Service Ports
- **Frontend**: 3000
- **Backend**: 8001
- **MCP Server**: 8000
- **PostgreSQL**: 5432

## 🔍 Monitoring and Debugging

### Logs
```bash
# Backend logs
docker-compose logs backend

# MCP server logs
docker-compose logs mcp-server

# All services
docker-compose logs -f
```

### Health Checks
- Backend: http://localhost:8001/health
- MCP Server: http://localhost:8000/health

## 🆘 Troubleshooting

- **OpenAI API Key**: Set `OPENAI_API_KEY` environment variable
- **Database**: Check `DATABASE_URL` configuration
- **MCP Server**: Verify server is running on port 8000
- **Frontend**: Clear node_modules and reinstall if build fails

