# file: query_processor.py
import asyncio
import uuid
import json
import traceback
from logger import logger
from typing import Dict, Optional, AsyncGenerator, Union, cast
from agno.agent import Agent, RunResponse
from mcp_agents import create_multi_agent, run_multimcp_agent, run_multimcp_agent_stream
from anyio import ClosedResourceError
from configure import load_server_config, get_llm_config
from agno.tools.mcp import MultiMCPTools
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama
from common_utils import initialize_embedder_and_vector_db, initialize_knowledge_base

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
        self.server_name = server_name
        logger.info(f"Starting initialization of QueryProcessor for server: {server_name}")
        try:
            # Initialize embedder and vector database
            self.vector_db, _ = initialize_embedder_and_vector_db(server_name)
            if not self.vector_db:
                raise Exception("Failed to initialize vector database")

            # Initialize knowledge base
            self.knowledge_base = initialize_knowledge_base(server_name, self.vector_db)

            # Initialize multi-agent
            self.agent = await create_multi_agent(server_name)
            if not self.agent:
                logger.warning(f"No valid agent found for {server_name}, query functionality may be limited")
            else:
                if self.knowledge_base:
                    self.agent.knowledge = self.knowledge_base
                    self.agent.search_knowledge = True
                    logger.info(f"Agent configured with combined knowledge base for {server_name}")

            # Verify LLM model
            llm_type, llm_model = get_llm_config(server_name)
            if llm_type == "ollama" and isinstance(self.agent.model, Ollama) and self.agent.model.id == llm_model:
                logger.info(f"Using Ollama model for {server_name}: {llm_model}")
            elif llm_type == "openai" and isinstance(self.agent.model, OpenAIChat) and self.agent.model.id == llm_model:
                logger.info(f"Using OpenAI model for {server_name}: {llm_model}")
            else:
                logger.warning(f"LLM configuration mismatch for {server_name}, using default Ollama model")
                self.agent.model = Ollama(id="hf.co/Qwen/Qwen3-0.6B-GGUF:latest")
        except Exception as e:
            logger.error(f"QueryProcessor initialization failed for {server_name}: {str(e)}")
            self.agent = None
            raise

    def start_session(self, session_id: Optional[str] = None) -> str:
        session_id = session_id or str(uuid.uuid4())
        self.sessions[session_id] = {
            "history": [],
            "context": {"history": []},
            "starting_agent": self.agent,
        }
        logger.info(f"Starting session: {session_id} for server {self.server_name}")
        return session_id

    def is_session_valid(self, session_id: str) -> bool:
        valid = session_id in self.sessions
        logger.info(f"Session validation {session_id} for server {self.server_name}: {'valid' if valid else 'invalid'}")
        return valid

    async def process_query(self, session_id: str, query: str) -> Dict[str, object]:
        if session_id not in self.sessions:
            logger.error(f"Session does not exist: {session_id} for server {self.server_name}")
            return {"error": "Session does not exist", "session_id": session_id}
        if not self.agent:
            logger.error(f"Agent not initialized for server {self.server_name}")
            return {"error": "Agent not initialized", "session_id": session_id}
        session = self.sessions[session_id]
        session["history"].append({"query": query})
        session["context"]["history"].append({"query": query})
        logger.info(f"Processing non-streaming query: {query}, session: {session_id} for server {self.server_name}")

        try:
            response = await run_multimcp_agent(query, self.server_name)
            if isinstance(response, dict) and "error" in response:
                return {"error": response["error"], "session_id": session_id}
            session["history"].append({"response": response})
            session["context"]["history"].append({"response": response})
            return {"response": response, "session_id": session_id, "complete": True}
        except asyncio.CancelledError as e:
            logger.error(f"Non-streaming query cancelled, session {session_id} for server {self.server_name}: {str(e)}")
            return {"error": f"Query cancelled: {str(e)}", "session_id": session_id}
        except Exception as e:
            if isinstance(e, ClosedResourceError):
                logger.info(f"Detected ClosedResourceError, attempting reinitialization, session {session_id} for server {self.server_name}")
                try:
                    await self.reinitialize()
                    return {"error": "Server resources closed, attempted reinitialization, please retry query", "session_id": session_id}
                except Exception as reinit_e:
                    logger.error(f"Reinitialization failed for server {self.server_name}: {str(reinit_e)}")
                    return {"error": f"Reinitialization failed: {str(reinit_e)}", "session_id": session_id}
            logger.error(f"Query processing error, session {session_id} for server {self.server_name}: type={type(e).__name__}, message={str(e)}")
            return {"error": f"Query processing failed: {str(e) or 'Unknown error'}", "session_id": session_id}

    async def reinitialize(self) -> None:
        logger.info(f"Start reinitialization of QueryProcessor for server {self.server_name}")
        try:
            self.agent = None
            self.vector_db = None
            self.knowledge_base = None
            await self.initialize(self.server_name)
            for session in self.sessions.values():
                session["starting_agent"] = self.agent
            logger.info(f"QueryProcessor reinitialization succeeded for server {self.server_name}, agent: {self.agent.name if self.agent else 'none'}")
        except asyncio.CancelledError:
            logger.warning(f"QueryProcessor reinitialization cancelled for server {self.server_name}")
            raise
        except Exception as e:
            logger.error(f"QueryProcessor reinitialization failed for server {self.server_name}: {str(e)}")
            self.agent = None
            raise

    async def _yield_error_response(self, code: int, message: str, request_id: Optional[int] = None) -> Dict:
        error_response = {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": request_id}
        logger.error(f"Generate streaming error response: {message} for server {self.server_name}")
        return error_response

    async def _yield_success_response(self, session_id: str, event_type: str, content: Union[str, Dict], complete: bool, request_id: Optional[int] = None) -> Dict:
        result = {"session_id": session_id, "type": event_type, "complete": complete}
        if event_type == "final":
            result["response"] = content
        else:
            result["content"] = content
        response = {"jsonrpc": "2.0", "result": result, "id": request_id}
        logger.info(f"Successfully generated streaming success response, type: {event_type}, complete: {complete} for server {self.server_name}")
        return response

    async def process_query_stream(self, session_id: str, query: str, request_id: Optional[int] = None) -> AsyncGenerator[Dict, None]:
        if session_id not in self.sessions:
            logger.error(f"Stream session does not exist: {session_id} for server {self.server_name}")
            yield await self._yield_error_response(
                code=-32600,
                message=f"Invalid session: {session_id}. Please call start_session to create a new session",
                request_id=request_id
            )
            return

        if not self.agent:
            logger.error(f"Agent not initialized for server {self.server_name}")
            yield await self._yield_error_response(
                code=-32603,
                message="Agent not initialized",
                request_id=request_id
            )
            return

        session = self.sessions[session_id]
        session["history"].append({"query": query})
        session["context"]["history"].append({"query": query})
        logger.info(f"Processing streaming query: {query}, session: {session_id} for server {self.server_name}")

        try:
            final_output = ""
            async for chunk in run_multimcp_agent_stream(query, self.server_name):
                chunk = cast(RunResponse, chunk)
                if hasattr(chunk, 'error') and chunk.error:
                    yield await self._yield_error_response(
                        code=-32603,
                        message=chunk.error,
                        request_id=request_id
                    )
                    return
                chunk_json = chunk.to_json()
                final_output += chunk_json + "\n"
                yield await self._yield_success_response(
                    session_id=session_id,
                    event_type="message",
                    content=chunk_json,
                    complete=False,
                    request_id=request_id
                )

            if final_output:
                session["history"].append({"response": final_output.strip()})
                session["context"]["history"].append({"response": final_output.strip()})
                yield await self._yield_success_response(
                    session_id=session_id,
                    event_type="final",
                    content=final_output.strip(),
                    complete=True,
                    request_id=request_id
                )
                logger.info(f"Stream query succeeded, session {session_id} for server {self.server_name}")
            else:
                logger.warning(f"Stream query produced no output, session {session_id} for server {self.server_name}")
                yield await self._yield_error_response(
                    code=-32603,
                    message="Stream query produced no valid output",
                    request_id=request_id
                )
        except Exception as e:
            logger.error(f"Stream query error, session {session_id} for server {self.server_name}: {str(e)}\n{traceback.format_exc()}")
            yield await self._yield_error_response(
                code=-32603,
                message=f"Stream query failed: {str(e)}",
                request_id=request_id
            )

    def end_session(self, session_id: str) -> Dict[str, str]:
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session ended: {session_id} for server {self.server_name}")
            return {"response": "Session ended", "session_id": session_id}
        logger.error(f"Session does not exist: {session_id} for server {self.server_name}")
        return {"error": "Session does not exist", "session_id": session_id}

    async def cleanup(self) -> None:
        logger.info(f"Start cleanup of QueryProcessor for server {self.server_name}")
        self.sessions.clear()
        self.agent = None
        self.vector_db = None
        self.knowledge_base = None
        logger.info(f"QueryProcessor cleanup completed for server {self.server_name}")