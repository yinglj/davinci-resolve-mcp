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
import io
from contextlib import redirect_stdout
from configure import load_server_config
from agno.tools.mcp import MultiMCPTools
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama

logger.debug("Loading query_processor module")

class QueryProcessor:
    def __init__(self):
        logger.debug("Initializing QueryProcessor")
        self.agent = None
        self.sessions: Dict[str, Dict] = {}

    async def initialize(self) -> None:
        logger.info("Starting initialization of QueryProcessor")
        try:
            self.agent = await create_multi_agent()
            if not self.agent:
                logger.warning("No valid agent found, query functionality may be limited")
            else:
                logger.info(f"QueryProcessor initialization successful, agent: {self.agent.name}")
        except Exception as e:
            logger.error(f"QueryProcessor initialization failed: {str(e)}")
            self.agent = None
            raise

    def start_session(self, session_id: Optional[str] = None) -> str:
        session_id = session_id or str(uuid.uuid4())
        self.sessions[session_id] = {
            "history": [],
            "context": {"history": []},
            "starting_agent": self.agent,
        }
        logger.info(f"Starting session: {session_id}")
        return session_id

    def is_session_valid(self, session_id: str) -> bool:
        valid = session_id in self.sessions
        logger.info(f"Session validation {session_id}: {'valid' if valid else 'invalid'}")
        return valid

    async def process_query(self, session_id: str, query: str) -> Dict[str, object]:
        if session_id not in self.sessions:
            logger.error(f"Session does not exist: {session_id}")
            return {"error": "Session does not exist", "session_id": session_id}
        if not self.agent:
            logger.error("Agent not initialized")
            return {"error": "Agent not initialized", "session_id": session_id}
        session = self.sessions[session_id]
        session["history"].append({"query": query})
        session["context"]["history"].append({"query": query})
        logger.info(f"Processing non-streaming query: {query}, session: {session_id}")

        try:
            response = await run_multimcp_agent(query, stream=True)
            return {
                "response": response,
                "session_id": session_id,
                "complete": True
            }
        except asyncio.CancelledError as e:
            logger.error(f"Non-streaming query cancelled, session {session_id}: {str(e)}")
            return {"error": f"Query cancelled: {str(e)}", "session_id": session_id}
        except Exception as e:
            if isinstance(e, ClosedResourceError):
                logger.info(f"Detected ClosedResourceError, attempting reinitialization, session {session_id}")
                try:
                    await self.reinitialize()
                    return {"error": "Server resources closed, attempted reinitialization, please retry query", "session_id": session_id}
                except Exception as reinit_e:
                    logger.error(f"Reinitialization failed: {str(reinit_e)}")
                    return {"error": f"Reinitialization failed: {str(reinit_e)}", "session_id": session_id}
            logger.error(f"Query processing error, session {session_id}: type={type(e).__name__}, message={str(e)}")
            return {"error": f"Query processing failed: {str(e) or 'Unknown error'}", "session_id": session_id}

    async def reinitialize(self) -> None:
        logger.info("Start reinitialization of QueryProcessor")
        try:
            self.agent = None
            self.agent = await create_multi_agent()
            if not self.agent:
                logger.warning("Reinitialization failed: no valid agent")
            for session in self.sessions.values():
                session["starting_agent"] = self.agent
            logger.info(f"QueryProcessor reinitialization succeeded, agent: {self.agent.name if self.agent else 'none'}")
        except asyncio.CancelledError:
            logger.warning("QueryProcessor was reinitialization cancelled")
            raise
        except Exception as e:
            logger.error(f"QueryProcessor reinitialization failed: {str(e)}")
            self.agent = None
            raise

    async def _yield_error_response(self, code: int, message: str, request_id: Optional[int] = None) -> Dict:
        error_response = {
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": request_id
        }
        logger.error(f"Generate streaming error response: {message}")
        return error_response

    async def _yield_success_response(
        self,
        session_id: str,
        event_type: str,
        content: Union[str, Dict],
        complete: bool,
        request_id: Optional[int] = None
    ) -> Dict:
        result = {
            "session_id": session_id,
            "type": event_type,
            "complete": complete
        }
        if event_type == "final":
            result["response"] = content
        else:
            result["content"] = content
        response = {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
        logger.info(f"Successfully generated streaming success response, type: {event_type}, complete: {complete}")
        return response

    async def process_query_stream(self, session_id: str, query: str, request_id: Optional[int] = None) -> AsyncGenerator[Dict, None]:
        if session_id not in self.sessions:
            logger.error(f"Stream session does not exist: {session_id}")
            yield await self._yield_error_response(
                code=-32600,
                message=f"Invalid session: {session_id}. Please call start_session to create a new session",
                request_id=request_id
            )
            return

        # Load server configurations
        server_configs = load_server_config()
        if not server_configs:
            logger.warning("There are no valid server configurations available for MultiMCPTools")
            yield await self._yield_error_response(
                code=-32603,
                message="There are no valid server configurations available for MultiMCPTools",
                request_id=request_id
            )
            return

        # Prepare commands and URLs for MultiMCPTools
        commands = []
        urls = []
        urls_transports = []

        for config in server_configs:
            try:
                name = config.get("name")
                command = config.get("command")
                args = config.get("args", [])
                if command == "sse" or command == "streamable-http":
                    if args and args[0].startswith("http"):
                        urls.append(args[0])
                        urls_transports.append(command)
                else:
                    commands.append(" ".join([command] + args))
            except Exception as e:
                logger.error(f"failed to process server config {name}: {str(e)}")
                continue

        if not commands and not urls:
            logger.warning("There are no valid server configurations available for MultiMCPTools")
            yield await self._yield_error_response(
                code=-32603,
                message="There are no valid server configurations available for MultiMCPTools",
                request_id=request_id
            )
            return

        try:
            # Create MultiMCPTools and Agent within the same async with block
            async with MultiMCPTools(
                commands=commands,
                urls=urls,
                urls_transports=urls_transports,
                timeout_seconds=int(max(config.get("timeout", 10) for config in server_configs)),
                # allow_partial_failure=True
            ) as mcp_tools:
                agent = Agent(
                    name="MultiMCPAgent",
                    instructions="You are a Davinci Resolve agent. Use the MCP tools to complete the user's queries.",
                    tools=[mcp_tools],
                    # model=OpenAIChat(id="gpt-4o"),
                    model=Ollama(id="hf.co/Qwen/Qwen3-0.6B-GGUF:latest"),
                    markdown=True,
                    add_datetime_to_instructions=True,
                    show_tool_calls=True,
                )
                # Start streaming and iterate over the response
                run_response = await agent.arun(query, stream=True, markdown=True, stream_intermediate_steps=False)
                content = ""
                final_output = ""
                async for run_response_chunk in run_response:
                    run_response_chunk = cast(RunResponse, run_response_chunk)
                    chunk_json = run_response_chunk.to_json()
                    content += chunk_json
                    yield await self._yield_success_response(
                        session_id=session_id,
                        event_type="message",
                        content=chunk_json,  # Yield each chunk separately
                        complete=False,
                        request_id=request_id
                    )
                    final_output += chunk_json + "\n"

                # After all chunks are processed, send the final response
                if final_output:

                    self.sessions[session_id]["history"].append({"response": final_output.strip()})
                    self.sessions[session_id]["context"]["history"].append({"response": final_output.strip()})
                    yield await self._yield_success_response(
                        session_id=session_id,
                        event_type="final",
                        content=final_output.strip(),
                        complete=True,
                        request_id=request_id
                    )
                    logger.info(f"Stream query succeeded, session {session_id}")
                else:
                    logger.warning(f"Stream query produced no output, session {session_id}")
                    yield await self._yield_error_response(
                        code=-32603,
                        message="Stream query produced no valid output",
                        request_id=request_id
                    )
        except Exception as e:
            logger.error(f"Stream query error, session {session_id}: {str(e)}\n{traceback.format_exc()}")
            yield await self._yield_error_response(
                code=-32603,
                message=f"Stream query failed: {str(e)}",
                request_id=request_id
            )

    def end_session(self, session_id: str) -> Dict[str, str]:
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session ended: {session_id}")
            return {"response": "Session ended", "session_id": session_id}
        logger.error(f"Session does not exist: {session_id}")
        return {"error": "Session does not exist", "session_id": session_id}

    async def cleanup(self) -> None:
        logger.info("Start cleanup of QueryProcessor")
        self.sessions.clear()
        self.agent = None
        logger.info("QueryProcessor cleanup completed")