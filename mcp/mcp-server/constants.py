#!/usr/bin/env python3
"""
Constants - Centralized configuration for LLM models and other constants
"""

# Standard library imports
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# LLM MODELS
# =============================================================================

# OpenAI Models (from environment variables)
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# PostgreSQL Configuration (from environment variables)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "camera_feeds")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# Database Connection URLs (for fallback)
POSTGRES_URLS = ["postgres", "localhost"]

# =============================================================================
# QDRANT CONFIGURATION
# =============================================================================

# Qdrant Configuration (from environment variables)
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION_NAME = "camera_data_chunks"

# Qdrant URLs (for fallback)
QDRANT_URLS = [os.getenv("QDRANT_URL", "http://qdrant:6333"), "http://localhost:6333"]

# =============================================================================
# RAG CONFIGURATION
# =============================================================================

# Text Chunking Configuration (from environment variables)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
CHUNK_SEPARATORS = ["\n\n", "\n", " ", ""]

# Retrieval Configuration (from environment variables)
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "10"))
MAX_TOP_K = 20

# =============================================================================
# DATA CONFIGURATION
# =============================================================================

# Data Directory (from environment variables)
DATA_DIR = os.getenv("DATA_DIR", "data")

# Supported File Types
SUPPORTED_FILE_TYPES = ["*.csv", "*.xlsx", "*.xls", "*.json"]

# =============================================================================
# SERVER CONFIGURATION
# =============================================================================

# MCP Server Configuration (from environment variables)
SERVER_NAME = os.getenv("SERVER_NAME", "mcp-query-server")
SERVER_VERSION = os.getenv("SERVER_VERSION", "1.0.0")

# =============================================================================
# ERROR MESSAGES
# =============================================================================

# Database Error Messages
DB_CONNECTION_ERROR = "Could not connect to database"
DB_QUERY_ERROR = "SQL Query Error"

# RAG Error Messages
RAG_NOT_INITIALIZED = "RAG system not initialized"
RAG_QUERY_ERROR = "Error executing RAG query"

# Data Error Messages
NO_DATA_FILES = "No data files found in data directory"
DATA_LOAD_ERROR = "Error loading data"
