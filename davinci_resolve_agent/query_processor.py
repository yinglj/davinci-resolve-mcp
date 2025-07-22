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

logger.debug("加载 query_processor 模块")

class QueryProcessor:
    def __init__(self):
        logger.debug("初始化 QueryProcessor")
        self.agent = None
        self.sessions: Dict[str, Dict] = {}

    async def initialize(self) -> None:
        logger.info("开始初始化 QueryProcessor")
        try:
            self.agent = await create_multi_agent()
            if not self.agent:
                logger.warning("没有有效的代理，查询功能可能受限")
            else:
                logger.info(f"QueryProcessor 初始化成功，代理: {self.agent.name}")
        except Exception as e:
            logger.error(f"QueryProcessor 初始化失败: {str(e)}")
            self.agent = None
            raise

    def start_session(self, session_id: Optional[str] = None) -> str:
        session_id = session_id or str(uuid.uuid4())
        self.sessions[session_id] = {
            "history": [],
            "context": {"history": []},
            "starting_agent": self.agent,
        }
        logger.info(f"开始会话: {session_id}")
        return session_id

    def is_session_valid(self, session_id: str) -> bool:
        valid = session_id in self.sessions
        logger.info(f"会话验证 {session_id}: {'有效' if valid else '无效'}")
        return valid

    async def process_query(self, session_id: str, query: str) -> Dict[str, object]:
        if session_id not in self.sessions:
            logger.error(f"会话不存在: {session_id}")
            return {"error": "会话不存在", "session_id": session_id}
        if not self.agent:
            logger.error("代理未初始化")
            return {"error": "代理未初始化", "session_id": session_id}
        session = self.sessions[session_id]
        session["history"].append({"query": query})
        session["context"]["history"].append({"query": query})
        logger.info(f"处理非流式查询: {query}，会话: {session_id}")

        try:
            response = await run_multimcp_agent(query, stream=True)
            return {
                "response": response,
                "session_id": session_id,
                "complete": True
            }
        except asyncio.CancelledError as e:
            logger.error(f"非流式查询被取消，会话 {session_id}: {str(e)}")
            return {"error": f"查询被取消: {str(e)}", "session_id": session_id}
        except Exception as e:
            if isinstance(e, ClosedResourceError):
                logger.info(f"检测到 ClosedResourceError，尝试重新初始化，会话 {session_id}")
                try:
                    await self.reinitialize()
                    return {"error": "服务器资源已关闭，已尝试重新初始化，请重试查询", "session_id": session_id}
                except Exception as reinit_e:
                    logger.error(f"重新初始化失败: {str(reinit_e)}")
                    return {"error": f"重新初始化失败: {str(reinit_e)}", "session_id": session_id}
            logger.error(f"查询处理错误，会话 {session_id}: type={type(e).__name__}, message={str(e)}")
            return {"error": f"查询处理失败: {str(e) or '未知错误'}", "session_id": session_id}

    async def reinitialize(self) -> None:
        logger.info("开始重新初始化 QueryProcessor")
        try:
            self.agent = None
            self.agent = await create_multi_agent()
            if not self.agent:
                logger.warning("重新初始化后没有有效的代理")
            for session in self.sessions.values():
                session["starting_agent"] = self.agent
            logger.info(f"QueryProcessor 重新初始化成功，代理: {self.agent.name if self.agent else '无'}")
        except asyncio.CancelledError:
            logger.warning("QueryProcessor 重新初始化被取消")
            raise
        except Exception as e:
            logger.error(f"QueryProcessor 重新初始化失败: {str(e)}")
            self.agent = None
            raise

    async def _yield_error_response(self, code: int, message: str, request_id: Optional[int] = None) -> Dict:
        error_response = {
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": request_id
        }
        logger.error(f"生成流式错误响应: {message}")
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
        logger.info(f"生成流式成功响应，类型: {event_type}, 完成: {complete}")
        return response

    async def process_query_stream(self, session_id: str, query: str, request_id: Optional[int] = None) -> AsyncGenerator[Dict, None]:
        if session_id not in self.sessions:
            logger.error(f"流式会话不存在: {session_id}")
            yield await self._yield_error_response(
                code=-32600,
                message=f"无效的会话: {session_id}。请调用 start_session 创建新会话",
                request_id=request_id
            )
            return

        # Load server configurations
        server_configs = load_server_config()
        if not server_configs:
            logger.warning("没有有效的服务器配置，无法创建代理")
            yield await self._yield_error_response(
                code=-32603,
                message="没有有效的服务器配置，无法创建代理",
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
                logger.error(f"处理服务器配置失败，服务器 {name}: {str(e)}")
                continue

        if not commands and not urls:
            logger.warning("没有有效的服务器配置可用于 MultiMCPTools")
            yield await self._yield_error_response(
                code=-32603,
                message="没有有效的服务器配置可用于 MultiMCPTools",
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
                    instructions="You are a database agent. Use the MCP tools to complete the user's queries.",
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
                    logger.info(f"流式查询成功完成，会话 {session_id}")
                else:
                    logger.warning(f"流式查询无输出，会话 {session_id}")
                    yield await self._yield_error_response(
                        code=-32603,
                        message="流式查询无有效输出",
                        request_id=request_id
                    )
        except Exception as e:
            logger.error(f"流式查询错误，会话 {session_id}: {str(e)}\n{traceback.format_exc()}")
            yield await self._yield_error_response(
                code=-32603,
                message=f"流式查询失败: {str(e)}",
                request_id=request_id
            )

    def end_session(self, session_id: str) -> Dict[str, str]:
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"结束会话: {session_id}")
            return {"response": "会话已结束", "session_id": session_id}
        logger.error(f"会话不存在: {session_id}")
        return {"error": "会话不存在", "session_id": session_id}

    async def cleanup(self) -> None:
        logger.info("开始清理 QueryProcessor")
        self.sessions.clear()
        self.agent = None
        logger.info("QueryProcessor 已清理")