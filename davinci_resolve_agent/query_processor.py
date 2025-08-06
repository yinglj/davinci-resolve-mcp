# file: query_processor.py
import asyncio
import uuid
import os
import json
import traceback
from logger import logger
from typing import Dict, Optional, AsyncGenerator, Union, cast
from pathlib import Path
from agno.agent import Agent, RunResponse
from mcp_agents import create_multi_agent, run_multimcp_agent, run_multimcp_agent_stream
from anyio import ClosedResourceError
from configure import load_server_config, load_knowledge_config, load_embedder_config, get_llm_config
from agno.tools.mcp import MultiMCPTools
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.pdf_bytes import PDFBytesKnowledgeBase
from agno.knowledge.markdown import MarkdownKnowledgeBase
from agno.knowledge.csv import CSVKnowledgeBase
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.embedder.ollama import OllamaEmbedder
from agno.embedder.openai import OpenAIEmbedder
import pyarrow as pa

logger.debug("Loading query_processor module")


class QueryProcessor:

    def __init__(self):
        logger.debug("Initializing QueryProcessor")
        self.agent = None
        self.sessions: Dict[str, Dict] = {}
        self.vector_db = None
        self.knowledge_base = None
        self.server_name = None

    async def initialize(self, server_name: str = "Davinci_resolve") -> None:
        """
        Initialize QueryProcessor with a specific server configuration.

        Args:
            server_name (str): The name of the server to initialize for.
        """
        self.server_name = server_name
        logger.info(
            f"Starting initialization of QueryProcessor for server: {server_name}"
        )
        try:
            # Load embedder configuration
            embedder_type, embedder_model, dimensions = load_embedder_config(
                server_name)
            if embedder_type == "ollama":
                embedder = OllamaEmbedder(id=embedder_model,
                                          dimensions=dimensions)
            elif embedder_type == "openai":
                embedder = OpenAIEmbedder(model=embedder_model,
                                          dimensions=dimensions)
            else:
                logger.error(
                    f"Unsupported embedder type {embedder_type} for server {server_name}, using default Ollama"
                )
                embedder = OllamaEmbedder(id=embedder_model,
                                          dimensions=dimensions)

            self.vector_db = LanceDb(
                table_name="knowledge_base",
                uri="tmp/lancedb",
                embedder=embedder,
            )
            logger.info(
                f"LanceDb initialized successfully with embedder: type={embedder_type}, model={embedder_model}, dimensions={dimensions}"
            )

            # Load knowledge files specific to the server
            knowledge_files = load_knowledge_config(server_name)
            logger.info(
                f"Loaded knowledge files for {server_name}: {knowledge_files}")
            if not knowledge_files:
                logger.warning(
                    f"No knowledge files loaded for {server_name}, proceeding without knowledge base"
                )
            else:
                pdf_files = []
                markdown_files = []
                csv_files = []
                text_files = []

                # Categorize files by extension
                for entry in knowledge_files:
                    file_path = entry["path"]
                    metadata = entry["metadata"]
                    if file_path.endswith(('.pdf', '.PDF')):
                        pdf_files.append({
                            "path": file_path,
                            "metadata": metadata
                        })
                    elif file_path.endswith('.md'):
                        markdown_files.append({
                            "path": file_path,
                            "metadata": metadata
                        })
                    elif file_path.endswith('.csv'):
                        csv_files.append({
                            "path": file_path,
                            "metadata": metadata
                        })
                    else:
                        # Treat all other files as text files
                        try:
                            # Try to open the file as text to verify it's readable
                            with open(file_path, 'r', encoding='utf-8') as f:
                                f.read(1024)  # Read first 1KB to check if readable
                            text_files.append({
                                "path": file_path,
                                "metadata": metadata
                            })
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
                        pdf_docs = []
                        for entry in pdf_files:
                            with open(entry["path"], "rb") as f:
                                pdf_docs.append(f.read())
                        pdf_kb = PDFBytesKnowledgeBase(
                            pdfs=pdf_docs,
                            texts=[],
                            vector_db=self.vector_db,
                        )
                        knowledge_bases.append(pdf_kb)
                        logger.info(
                            f"Initialized PDFBytesKnowledgeBase with {len(pdf_docs)} PDF documents for {server_name}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to initialize PDF knowledge base for {server_name}: {str(e)}"
                        )

                # Create Markdown knowledge base
                if markdown_files:
                    try:
                        markdown_kb = MarkdownKnowledgeBase(
                            path=[{
                                "path": entry["path"],
                                "metadata": entry["metadata"]
                            } for entry in markdown_files],
                            vector_db=self.vector_db,
                            num_documents=
                            5,  # Number of documents to return on search
                        )
                        knowledge_bases.append(markdown_kb)
                        logger.info(
                            f"Initialized MarkdownKnowledgeBase with {len(markdown_files)} Markdown documents for {server_name}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to initialize Markdown knowledge base for {server_name}: {str(e)}"
                        )

                # Create CSV knowledge base
                if csv_files:
                    try:
                        csv_kb = CSVKnowledgeBase(
                            path=[{
                                "path": entry["path"],
                                "metadata": entry["metadata"]
                            } for entry in csv_files],
                            vector_db=self.vector_db,
                        )
                        knowledge_bases.append(csv_kb)
                        logger.info(
                            f"Initialized CSVKnowledgeBase with {len(csv_files)} CSV documents for {server_name}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to initialize CSV knowledge base for {server_name}: {str(e)}"
                        )

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

                # Combine knowledge bases
                if knowledge_bases:
                    try:
                        self.knowledge_base = CombinedKnowledgeBase(
                            sources=knowledge_bases,
                            vector_db=self.vector_db,
                        )
                        await self.knowledge_base.aload(recreate=False)
                        logger.info(
                            f"Combined knowledge base loaded with {len(knowledge_bases)} sources for {server_name}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to load combined knowledge base for {server_name}: {str(e)}"
                        )
                        try:
                            await self.knowledge_base.aload(recreate=True)
                            logger.info(
                                f"Combined knowledge base recreated and loaded successfully for {server_name}"
                            )
                        except Exception as reinit_e:
                            logger.error(
                                f"Combined knowledge base recreation failed: {str(reinit_e)}"
                            )
                            self.knowledge_base = None

            # Initialize multi-agent
            self.agent = await create_multi_agent(server_name)
            if not self.agent:
                logger.warning(
                    f"No valid agent found for {server_name}, query functionality may be limited"
                )
            else:
                logger.info(
                    f"QueryProcessor initialization successful for {server_name}, agent: {self.agent.name}"
                )
                if self.knowledge_base:
                    self.agent.knowledge = self.knowledge_base
                    self.agent.search_knowledge = True
                    logger.info(
                        f"Agent configured with combined knowledge base for {server_name}"
                    )

            # Verify LLM model
            llm_type, llm_model = get_llm_config(server_name)
            if llm_type == "ollama" and isinstance(
                    self.agent.model,
                    Ollama) and self.agent.model.id == llm_model:
                logger.info(
                    f"Using Ollama model for {server_name}: {llm_model}")
            elif llm_type == "openai" and isinstance(
                    self.agent.model,
                    OpenAIChat) and self.agent.model.id == llm_model:
                logger.info(
                    f"Using OpenAI model for {server_name}: {llm_model}")
            else:
                logger.warning(
                    f"LLM configuration mismatch for {server_name}, using default Ollama model"
                )
                self.agent.model = Ollama(
                    id="hf.co/Qwen/Qwen3-0.6B-GGUF:latest")
        except Exception as e:
            logger.error(
                f"QueryProcessor initialization failed for {server_name}: {str(e)}"
            )
            self.agent = None
            raise

    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new session.

        Args:
            session_id (Optional[str]): Optional session ID, generates a new one if not provided.

        Returns:
            str: The session ID.
        """
        session_id = session_id or str(uuid.uuid4())
        self.sessions[session_id] = {
            "history": [],
            "context": {
                "history": []
            },
            "starting_agent": self.agent,
        }
        logger.info(
            f"Starting session: {session_id} for server {self.server_name}")
        return session_id

    def is_session_valid(self, session_id: str) -> bool:
        """
        Check if a session is valid.

        Args:
            session_id (str): The session ID to validate.

        Returns:
            bool: True if the session is valid, False otherwise.
        """
        valid = session_id in self.sessions
        logger.info(
            f"Session validation {session_id} for server {self.server_name}: {'valid' if valid else 'invalid'}"
        )
        return valid

    async def process_query(self, session_id: str,
                            query: str) -> Dict[str, object]:
        """
        Process a non-streaming query.

        Args:
            session_id (str): The session ID.
            query (str): The query to process.

        Returns:
            Dict[str, object]: The query response or error.
        """
        if session_id not in self.sessions:
            logger.error(
                f"Session does not exist: {session_id} for server {self.server_name}"
            )
            return {
                "error": "Session does not exist",
                "session_id": session_id
            }
        if not self.agent:
            logger.error(
                f"Agent not initialized for server {self.server_name}")
            return {"error": "Agent not initialized", "session_id": session_id}
        session = self.sessions[session_id]
        session["history"].append({"query": query})
        session["context"]["history"].append({"query": query})
        logger.info(
            f"Processing non-streaming query: {query}, session: {session_id} for server {self.server_name}"
        )

        try:
            response = await run_multimcp_agent(query, self.server_name)
            if isinstance(response, dict) and "error" in response:
                return {"error": response["error"], "session_id": session_id}
            session["history"].append({"response": response})
            session["context"]["history"].append({"response": response})
            return {
                "response": response,
                "session_id": session_id,
                "complete": True
            }
        except asyncio.CancelledError as e:
            logger.error(
                f"Non-streaming query cancelled, session {session_id} for server {self.server_name}: {str(e)}"
            )
            return {
                "error": f"Query cancelled: {str(e)}",
                "session_id": session_id
            }
        except Exception as e:
            if isinstance(e, ClosedResourceError):
                logger.info(
                    f"Detected ClosedResourceError, attempting reinitialization, session {session_id} for server {self.server_name}"
                )
                try:
                    await self.reinitialize()
                    return {
                        "error":
                        "Server resources closed, attempted reinitialization, please retry query",
                        "session_id": session_id
                    }
                except Exception as reinit_e:
                    logger.error(
                        f"Reinitialization failed for server {self.server_name}: {str(reinit_e)}"
                    )
                    return {
                        "error": f"Reinitialization failed: {str(reinit_e)}",
                        "session_id": session_id
                    }
            logger.error(
                f"Query processing error, session {session_id} for server {self.server_name}: type={type(e).__name__}, message={str(e)}"
            )
            return {
                "error":
                f"Query processing failed: {str(e) or 'Unknown error'}",
                "session_id": session_id
            }

    async def reinitialize(self) -> None:
        """
        Reinitialize the QueryProcessor.

        Raises:
            Exception: If reinitialization fails.
        """
        logger.info(
            f"Start reinitialization of QueryProcessor for server {self.server_name}"
        )
        try:
            self.agent = None
            self.vector_db = None
            self.knowledge_base = None
            await self.initialize(self.server_name)
            for session in self.sessions.values():
                session["starting_agent"] = self.agent
            logger.info(
                f"QueryProcessor reinitialization succeeded for server {self.server_name}, agent: {self.agent.name if self.agent else 'none'}"
            )
        except asyncio.CancelledError:
            logger.warning(
                f"QueryProcessor reinitialization cancelled for server {self.server_name}"
            )
            raise
        except Exception as e:
            logger.error(
                f"QueryProcessor reinitialization failed for server {self.server_name}: {str(e)}"
            )
            self.agent = None
            raise

    async def _yield_error_response(self,
                                    code: int,
                                    message: str,
                                    request_id: Optional[int] = None) -> Dict:
        """
        Yield an error response for streaming.

        Args:
            code (int): Error code.
            message (str): Error message.
            request_id (Optional[int]): Request ID.

        Returns:
            Dict: Error response dictionary.
        """
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }
        logger.error(
            f"Generate streaming error response: {message} for server {self.server_name}"
        )
        return error_response

    async def _yield_success_response(
            self,
            session_id: str,
            event_type: str,
            content: Union[str, Dict],
            complete: bool,
            request_id: Optional[int] = None) -> Dict:
        """
        Yield a success response for streaming.

        Args:
            session_id (str): The session ID.
            event_type (str): The event type (e.g., "message", "final").
            content (Union[str, Dict]): The response content.
            complete (bool): Whether the response is complete.
            request_id (Optional[int]): Request ID.

        Returns:
            Dict: Success response dictionary.
        """
        result = {
            "session_id": session_id,
            "type": event_type,
            "complete": complete
        }
        if event_type == "final":
            result["response"] = content
        else:
            result["content"] = content
        response = {"jsonrpc": "2.0", "result": result, "id": request_id}
        logger.info(
            f"Successfully generated streaming success response, type: {event_type}, complete: {complete} for server {self.server_name}"
        )
        return response

    async def process_query_stream(
            self,
            session_id: str,
            query: str,
            request_id: Optional[int] = None) -> AsyncGenerator[Dict, None]:
        """
        Process a streaming query.

        Args:
            session_id (str): The session ID.
            query (str): The query to process.
            request_id (Optional[int]): Request ID.

        Yields:
            Dict: Streamed response or error.
        """
        if session_id not in self.sessions:
            logger.error(
                f"Stream session does not exist: {session_id} for server {self.server_name}"
            )
            yield await self._yield_error_response(
                code=-32600,
                message=
                f"Invalid session: {session_id}. Please call start_session to create a new session",
                request_id=request_id)
            return

        if not self.agent:
            logger.error(
                f"Agent not initialized for server {self.server_name}")
            yield await self._yield_error_response(
                code=-32603,
                message="Agent not initialized",
                request_id=request_id)
            return

        session = self.sessions[session_id]
        session["history"].append({"query": query})
        session["context"]["history"].append({"query": query})
        logger.info(
            f"Processing streaming query: {query}, session: {session_id} for server {self.server_name}"
        )

        try:
            final_output = ""
            async for chunk in run_multimcp_agent_stream(
                    query, self.server_name):
                chunk = cast(RunResponse, chunk)
                if hasattr(chunk, 'error') and chunk.error:
                    yield await self._yield_error_response(
                        code=-32603,
                        message=chunk.error,
                        request_id=request_id)
                    return
                chunk_json = chunk.to_json()
                final_output += chunk_json + "\n"
                yield await self._yield_success_response(session_id=session_id,
                                                         event_type="message",
                                                         content=chunk_json,
                                                         complete=False,
                                                         request_id=request_id)

            if final_output:
                session["history"].append({"response": final_output.strip()})
                session["context"]["history"].append(
                    {"response": final_output.strip()})
                yield await self._yield_success_response(
                    session_id=session_id,
                    event_type="final",
                    content=final_output.strip(),
                    complete=True,
                    request_id=request_id)
                logger.info(
                    f"Stream query succeeded, session {session_id} for server {self.server_name}"
                )
            else:
                logger.warning(
                    f"Stream query produced no output, session {session_id} for server {self.server_name}"
                )
                yield await self._yield_error_response(
                    code=-32603,
                    message="Stream query produced no valid output",
                    request_id=request_id)
        except Exception as e:
            logger.error(
                f"Stream query error, session {session_id} for server {self.server_name}: {str(e)}\n{traceback.format_exc()}"
            )
            yield await self._yield_error_response(
                code=-32603,
                message=f"Stream query failed: {str(e)}",
                request_id=request_id)

    def end_session(self, session_id: str) -> Dict[str, str]:
        """
        End a session.

        Args:
            session_id (str): The session ID to end.

        Returns:
            Dict[str, str]: Response indicating session status.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(
                f"Session ended: {session_id} for server {self.server_name}")
            return {"response": "Session ended", "session_id": session_id}
        logger.error(
            f"Session does not exist: {session_id} for server {self.server_name}"
        )
        return {"error": "Session does not exist", "session_id": session_id}

    async def cleanup(self) -> None:
        """
        Clean up QueryProcessor resources.
        """
        logger.info(
            f"Start cleanup of QueryProcessor for server {self.server_name}")
        self.sessions.clear()
        self.agent = None
        self.vector_db = None
        self.knowledge_base = None
        logger.info(
            f"QueryProcessor cleanup completed for server {self.server_name}")
