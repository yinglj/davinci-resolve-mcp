# file: common_utils.py
"""
Common utility functions for knowledge base and embedder initialization.
"""
import asyncio
import traceback
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from agno.knowledge import Knowledge
from agno.knowledge.embedder.ollama import OllamaEmbedder
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb
from agno.db.sqlite.sqlite import SqliteDb
from configure import load_embedder_config, load_knowledge_config
from logger import logger

def initialize_embedder_and_vector_db(server_name: str) -> tuple[Optional[LanceDb], Optional[SqliteDb], Optional[OllamaEmbedder | OpenAIEmbedder]]:
    """Initialize embedder and vector database based on server configuration."""
    try:
        embedder_type, embedder_model, dimensions = load_embedder_config(server_name)
        if embedder_type == "ollama":
            embedder = OllamaEmbedder(id=embedder_model, dimensions=dimensions)
        elif embedder_type == "openai":
            embedder = OpenAIEmbedder(model=embedder_model, dimensions=dimensions)
        else:
            logger.error(f"Unsupported embedder type {embedder_type}, defaulting to Ollama")
            embedder = OllamaEmbedder(id="hf.co/jinaai/jina-embeddings-v4-text-retrieval-GGUF:Q4_K_M", dimensions=2048)

        vector_db = LanceDb(
            table_name="knowledge_base",
            uri="tmp/lancedb",
            embedder=embedder,
        )
        content_db = SqliteDb(session_table="knowledge_base", db_file="tmp/knowledge_base.db")
        logger.info(f"Initialized LanceDb with embedder: type={embedder_type}, model={embedder_model}, dimensions={dimensions}")
        return vector_db, content_db, embedder 
    except Exception as e:
        logger.error(f"Failed to initialize embedder and vector db for {server_name}: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        return None, None, None

async def initialize_knowledge_base(server_name: str, vector_db: LanceDb, content_db: SqliteDb) -> Optional[Knowledge]:
    """Initialize knowledge base from configured files using agno 2.0 Knowledge API."""
    try:
        # Create the main Knowledge instance
        knowledge = Knowledge(
            name=server_name,
            vector_db=vector_db,
            contents_db=content_db,
            max_results=10
        )

        # Load knowledge files configuration
        knowledge_files = load_knowledge_config(server_name)
        if not knowledge_files:
            logger.warning(f"No knowledge files loaded for {server_name}")
            return knowledge

        logger.info(f"Starting to add {len(knowledge_files)} knowledge files for {server_name}")
        
        # Track added files to detect duplicates
        processed_files = set()
        
        # Add each configured file to the knowledge base
        for index, entry in enumerate(knowledge_files, 1):
            file_path = entry["path"]
            metadata = entry["metadata"]
            
            # Detect if the same file is being added multiple times
            if file_path in processed_files:
                logger.warning(f"Duplicate file detected in knowledge configuration: {file_path}, skipping")
                continue
            processed_files.add(file_path)
            
            try:
                logger.info(f"[{index}/{len(knowledge_files)}] Adding content from {file_path} to knowledge base")
                await knowledge.add_content_async(
                    path=file_path,
                    metadata=metadata,
                    upsert=True,
                    skip_if_exists=True
                )
                logger.debug(f"Successfully added {file_path}")
            except Exception as e:
                logger.error(f"Failed to add content from {file_path}: {str(e)}")
                logger.debug(f"Stack trace: {traceback.format_exc()}")
                continue

        logger.info(f"Successfully initialized knowledge base for {server_name} with {len(processed_files)} unique files")
        return knowledge

    except Exception as e:
        logger.error(f"Failed to initialize knowledge base for {server_name}: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        return None