# MCP Server - Camera Feed Query System

This MCP (Model Context Protocol) server provides tools for querying camera feed data, encoder/decoder schemas, and performing RAG-based information retrieval.

## Overview

The MCP server exposes two main tools:
- **`rag_query_tool`** - Retrieves relevant metadata and schema information
- **`sql_query_tool`** - Executes SQL queries against the camera feeds database

## Architecture

```
MCP Server
├── server.py          # Main MCP server implementation
├── tools.py           # Tool definitions and implementations
├── database-service.py # Database connection and query handling
├── rag_service.py     # RAG (Retrieval Augmented Generation) service
├── config.py          # Configuration management
└── constants.py       # Application constants
```

## Features

### RAG Query Tool
- Retrieves relevant information about camera feeds, encoders, and decoders
- Uses vector similarity search for context-aware responses
- Provides metadata for SQL query formation

### SQL Query Tool
- Executes SQL queries against PostgreSQL database
- Supports complex queries with joins and aggregations
- Returns formatted results for LLM consumption

## Database Schema

The server connects to a PostgreSQL database with the following main table:

**camera_feeds** - Contains 100 camera feed records with fields:
- `feed_id` - Unique camera identifier
- `theater` - Geographic region (PAC, ME, AFR, CONUS, EUR)
- `frrate` - Frame rate
- `res_w`, `res_h` - Resolution width and height
- `codec` - Video codec (H264, H265, AV1, VP9, MPEG2)
- `encr` - Encryption status
- `lat_ms` - Latency in milliseconds
- `modl_tag` - Model tag
- `civ_ok` - Civilian operation status

## Configuration

Set the following environment variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# RAG Configuration
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=camera_feeds

# Server Configuration
MCP_SERVER_PORT=8000
```

## Running the Server

### Using Docker Compose (Recommended)

```bash
cd mcp/mcp-server
docker-compose up -d
```

### Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python server.py
```

## API Endpoints

The server exposes HTTP endpoints for tool execution:

- **POST /tools/call** - Execute MCP tools
  ```json
  {
    "name": "rag_query_tool",
    "arguments": {
      "query": "What are the available regions?"
    }
  }
  ```

## MCP Protocol Support

The server supports both:
- **MCP stdio protocol** - For direct MCP client connections
- **HTTP protocol** - For web-based integrations

## Integration with LangGraph

This MCP server is designed to work with the LangGraph-based chatbot system:

1. **MCP Client** connects to this server via HTTP
2. **RAG Tool** provides context for query understanding
3. **SQL Tool** executes data queries based on RAG results
4. **Results** are returned to the LangGraph workflow

## Development

### Adding New Tools

1. Define the tool in `tools.py`
2. Implement the tool logic
3. Register the tool in `server.py`
4. Update this README

### Testing

```bash
# Test RAG tool
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "rag_query_tool", "arguments": {"query": "test query"}}'

# Test SQL tool
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "sql_query_tool", "arguments": {"query": "SELECT COUNT(*) FROM camera_feeds"}}'
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check `DATABASE_URL` environment variable
   - Ensure PostgreSQL is running and accessible

2. **Qdrant Connection Failed**
   - Verify `QDRANT_URL` is correct
   - Ensure Qdrant service is running

3. **Tool Execution Errors**
   - Check server logs for detailed error messages
   - Verify tool arguments are properly formatted

## Dependencies

- FastAPI - Web framework
- PostgreSQL - Database
- Qdrant - Vector database for RAG
- LangChain - LLM integration
- Pydantic - Data validation

See `requirements.txt` for complete dependency list.
