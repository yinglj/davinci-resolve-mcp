# file: common_utils.py
"""
Common utility functions for knowledge base and embedder initialization.
"""
import asyncio
import traceback
from typing import List, Dict, Optional
from pathlib import Path
from agno.embedder.ollama import OllamaEmbedder
from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.pdf_bytes import PDFBytesKnowledgeBase
from agno.knowledge.markdown import MarkdownKnowledgeBase
from agno.knowledge.csv import CSVKnowledgeBase
from agno.knowledge.text import TextKnowledgeBase
from agno.knowledge.combined import CombinedKnowledgeBase
from configure import load_embedder_config, load_knowledge_config
from logger import logger

def initialize_embedder_and_vector_db(server_name: str) -> tuple[Optional[LanceDb], Optional[OllamaEmbedder | OpenAIEmbedder]]:
    """
    Initialize embedder and vector database based on server configuration.

    Returns:
        tuple[Optional[LanceDb], Optional[OllamaEmbedder | OpenAIEmbedder]]: Vector DB and embedder instance.
    """
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
        logger.info(f"Initialized LanceDb with embedder: type={embedder_type}, model={embedder_model}, dimensions={dimensions}")
        return vector_db, embedder
    except Exception as e:
        logger.error(f"Failed to initialize embedder and vector db for {server_name}: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        return None, None

async def initialize_knowledge_base(server_name: str, vector_db: LanceDb) -> Optional[CombinedKnowledgeBase]:
    """
    Initialize knowledge base from configured files.

    Returns:
        Optional[CombinedKnowledgeBase]: Combined knowledge base instance.
    """
    knowledge_files = load_knowledge_config(server_name)
    if not knowledge_files:
        logger.warning(f"No knowledge files loaded for {server_name}")
        return None

    pdf_files = []
    markdown_files = []
    csv_files = []
    text_files = []

    # Categorize files by extension
    for entry in knowledge_files:
        file_path = entry["path"]
        metadata = entry["metadata"]
        if file_path.endswith(('.pdf', '.PDF')):
            pdf_files.append({"path": file_path, "metadata": metadata})
        elif file_path.endswith('.md'):
            markdown_files.append({"path": file_path, "metadata": metadata})
        elif file_path.endswith('.csv'):
            csv_files.append({"path": file_path, "metadata": metadata})
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(1024)
                text_files.append({"path": file_path, "metadata": metadata})
                if not file_path.endswith('.txt'):
                    logger.info(f"Treating file as text: {file_path}")
            except UnicodeDecodeError:
                logger.warning(f"File cannot be read as text: {file_path}")
            except Exception as e:
                logger.warning(f"Error processing file {file_path}: {str(e)}")

    knowledge_bases = []

    # Create PDF knowledge base
    if pdf_files:
        try:
            pdf_docs = [Path(entry["path"]).read_bytes() for entry in pdf_files]
            pdf_kb = PDFBytesKnowledgeBase(pdfs=pdf_docs, texts=[], vector_db=vector_db)
            knowledge_bases.append(pdf_kb)
            logger.info(f"Initialized PDFBytesKnowledgeBase with {len(pdf_docs)} PDF documents for {server_name}")
        except Exception as e:
            logger.error(f"Failed to initialize PDF knowledge base for {server_name}: {str(e)}")

    # Create Markdown knowledge base
    if markdown_files:
        try:
            markdown_kb = MarkdownKnowledgeBase(
                path=[{"path": entry["path"], "metadata": entry["metadata"]} for entry in markdown_files],
                vector_db=vector_db,
                num_documents=5,
            )
            knowledge_bases.append(markdown_kb)
            logger.info(f"Initialized MarkdownKnowledgeBase with {len(markdown_files)} Markdown documents for {server_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Markdown knowledge base for {server_name}: {str(e)}")

    # Create CSV knowledge base
    if csv_files:
        try:
            csv_kb = CSVKnowledgeBase(
                path=[{"path": entry["path"], "metadata": entry["metadata"]} for entry in csv_files],
                vector_db=vector_db,
            )
            knowledge_bases.append(csv_kb)
            logger.info(f"Initialized CSVKnowledgeBase with {len(csv_files)} CSV documents for {server_name}")
        except Exception as e:
            logger.error(f"Failed to initialize CSV knowledge base for {server_name}: {str(e)}")

    # Create Text knowledge base
    if text_files:
        try:
            text_kb = TextKnowledgeBase(
                path=[{"path": entry["path"], "metadata": entry["metadata"]} for entry in text_files],
                vector_db=vector_db,
            )
            knowledge_bases.append(text_kb)
            logger.info(f"Initialized TextKnowledgeBase with {len(text_files)} text documents for {server_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Text knowledge base for {server_name}: {str(e)}")

    if knowledge_bases:
        try:
            knowledge_base = CombinedKnowledgeBase(sources=knowledge_bases, vector_db=vector_db)
            await knowledge_base.aload(recreate=False)
            logger.info(f"Combined knowledge base loaded with {len(knowledge_bases)} sources for {server_name}")
            return knowledge_base
        except Exception as e:
            logger.error(f"Failed to load combined knowledge base for {server_name}: {str(e)}")
            try:
                await knowledge_base.aload(recreate=True)
                logger.info(f"Combined knowledge base recreated and loaded for {server_name}")
                return knowledge_base
            except Exception as reinit_e:
                logger.error(f"Combined knowledge base recreation failed: {str(reinit_e)}")
                return None
    return None