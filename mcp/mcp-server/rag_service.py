#!/usr/bin/env python3
"""
RAG Utilities - Data loading, chunking, and vector store management
"""

# Standard library imports
import json
import os
from pathlib import Path
from typing import List, Dict, Any

# Third-party imports
import pandas as pd
import requests
from qdrant_client import QdrantClient

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate

# Local imports
from constants import (
    OPENAI_CHAT_MODEL, OPENAI_EMBEDDING_MODEL,
    QDRANT_URLS, QDRANT_COLLECTION_NAME,
    CHUNK_SIZE, CHUNK_OVERLAP, CHUNK_SEPARATORS,
    DEFAULT_TOP_K, DATA_DIR, SUPPORTED_FILE_TYPES,
    NO_DATA_FILES, DATA_LOAD_ERROR
)

# =============================================================================
# DATA LOADING & CHUNKING
# =============================================================================

def load_data_from_directory(data_dir: str) -> List[str]:
    """Load all supported files from data directory and return as text chunks"""
    texts = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"Data directory {data_dir} does not exist")
        return texts

    # Load all supported file types
    for pattern in SUPPORTED_FILE_TYPES:
        for file_path in data_path.glob(pattern):
            texts.extend(load_from_file(str(file_path)))

    return texts

def load_from_file(file_path: str) -> List[str]:
    """Load data from a single file (CSV, XLSX, JSON)"""
    texts = []
    path = Path(file_path)
    
    if not path.exists():
        return texts
    
    try:
        if path.suffix.lower() == '.csv':
            df = pd.read_csv(path)
            texts.append(f"File: {path.name}\n{df.to_csv(index=False)}")
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(path)
            texts.append(f"File: {path.name}\n{df.to_csv(index=False)}")
        elif path.suffix.lower() == '.json':
            with open(path, 'r') as file:
                data = json.load(file)
            texts.append(f"File: {path.name}\n{json.dumps(data, indent=2)}")
        
        print(f"Loaded {path.suffix.upper()}: {path.name}")
    except Exception as e:
        print(f"{DATA_LOAD_ERROR}: {path.name}: {e}")
    
    return texts

def chunk_texts(texts: List[str]) -> List[Document]:
    """Split texts into smaller chunks for better embeddings"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
        length_function=len, separators=CHUNK_SEPARATORS
    )
    docs = splitter.create_documents(texts)
    print(f"Created {len(docs)} text chunks")
    return docs

# =============================================================================
# QDRANT VECTOR STORE
# =============================================================================

def get_qdrant_url() -> str:
    """Get Qdrant URL - try Docker first, then localhost"""
    for url in QDRANT_URLS:
        try:
            response = requests.get(f"{url}/collections", timeout=2)
            if response.status_code == 200:
                return url
        except:
            continue
    return QDRANT_URLS[-1]  # fallback to last URL

def build_vectorstore(docs: List[Document]) -> Qdrant:
    """Build Qdrant vector store from documents"""
    try:
        embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
        collection_name = QDRANT_COLLECTION_NAME
        qdrant_url = get_qdrant_url()
        
        vectorstore = Qdrant.from_documents(
            docs, embeddings, url=qdrant_url,
            collection_name=collection_name, force_recreate=True
        )
        
        print(f"Qdrant vector store built with {len(docs)} documents at {qdrant_url}")
        return vectorstore
    except Exception as e:
        print(f"Error building Qdrant vector store: {e}")
        raise

def load_existing_vectorstore() -> Qdrant:
    """Load existing Qdrant collection"""
    try:
        embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
        collection_name = QDRANT_COLLECTION_NAME
        qdrant_url = get_qdrant_url()
        
        # Check if collection exists first
        client = QdrantClient(url=qdrant_url)
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if collection_name not in collection_names:
            print(f"Collection {collection_name} does not exist, will create new one")
            return None
        
        vectorstore = Qdrant(
            client=client,
            collection_name=collection_name, embeddings=embeddings
        )
        
        print(f"Loaded existing Qdrant collection: {collection_name}")
        return vectorstore
    except Exception as e:
        print(f"Error loading existing Qdrant collection: {e}")
        return None

# =============================================================================
# RAG SYSTEM
# =============================================================================

# Global RAG instance
_rag_instance = None

def get_rag_instance() -> RetrievalQA:
    """Get or create RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        # Try to load existing collection first
        vectorstore = load_existing_vectorstore()
        if vectorstore is None:
            # Create new collection from data
            print("Creating new RAG system from data...")
            texts = load_data_from_directory(DATA_DIR)
            if not texts:
                print(NO_DATA_FILES)
                return None
            
            docs = chunk_texts(texts)
            vectorstore = build_vectorstore(docs)
        
        # Create RAG pipeline with custom prompt
        retriever = vectorstore.as_retriever(search_kwargs={"k": DEFAULT_TOP_K})
        llm = ChatOpenAI(model=OPENAI_CHAT_MODEL, temperature=0)
        
        # Custom prompt template for better responses
        prompt_template = """Use the following pieces of context to answer the question at the end. 
        Analyze the provided context and infer relevant information from the available data fields and their descriptions.
        If asked about quality criteria, quality assessment, or how to determine quality, examine the context 
        to identify which fields might indicate quality and how they could be used for assessment.
        
        Context:
        {context}

        Question: {question}
        
        Answer: Based on the available data fields and their descriptions, provide a comprehensive answer."""
        
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        
        _rag_instance = RetrievalQA.from_chain_type(
            llm=llm, retriever=retriever, 
            chain_type="stuff", return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        print("RAG system ready!")
    
    return _rag_instance
