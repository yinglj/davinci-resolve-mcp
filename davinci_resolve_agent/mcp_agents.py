# file: mcp_agents.py
import traceback
from agno.agent import Agent, RunResponse
from typing import cast
from agno.tools.mcp import MultiMCPTools
from logger import logger
from configure import load_server_config
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama
from agno.agent import Memory

async def create_multi_agent() -> Agent:
    server_configs = load_server_config()
    if not server_configs:
        logger.warning("没有有效的服务器配置，无法创建代理")
        return None

    commands = []
    urls = []
    urls_transports = []

    logger.debug(f"Processing {len(server_configs)} server configurations: {[c['name'] for c in server_configs]}")
    for config in server_configs:
        try:
            name = config.get("name")
            command = config.get("command")
            args = config.get("args", [])
            timeout = config.get("timeout", 10)
            
            if not name or not command:
                logger.error(f"Invalid configuration for server '{name}': {config}")
                continue

            if command == "sse" or command == "streamable-http":
                if not args[0].startswith("http"):
                    logger.error(f"Invalid SSE configuration for server '{name}': args must contain a valid HTTP URL")
                    continue
                urls.append(args[0])
                urls_transports.append(command)
                logger.info(f"Added SSE server: {name}, url: {args[0]}, urls_transports: {urls_transports}")
            else:
                commands.append(" ".join([command] + args))
                logger.info(f"Added Stdio server: {name}, command: {' '.join([command] + args)}")
        except Exception as e:
            logger.error(f"处理服务器配置失败，服务器 {name}: {str(e)}")
            logger.info(f"Stack trace: {traceback.format_exc()}")
            continue

    if not commands and not urls:
        logger.warning("没有有效的服务器配置可用于 MultiMCPTools")
        return None

    try:
        # Create MultiMCPTools and Agent within the same async with block
        logger.info("Creating MultiMCPTools and Agent..., commands: %s, urls: %s, urls_transports: %s",
                    commands, urls, urls_transports)
        async with MultiMCPTools(
            commands=commands,
            urls=urls,
            urls_transports=urls_transports,
            timeout_seconds=int(max(config.get("timeout", 10) for config in server_configs)),
            # allow_partial_failure=True
        ) as mcp_tools:
            function_names = [getattr(f, 'name', key) for key, f in mcp_tools.functions.items()]
            agent = Agent(
                name="MultiMCPAgent",
                instructions="You are a database agent. Use the MCP tools to complete the user's queries.",
                tools=[mcp_tools],
                model=OpenAIChat(id="gpt-4o"),
                markdown=True,
                add_datetime_to_instructions=True,
            )
            logger.info(f"创建代理: {agent.name}，工具: {function_names}")
            return agent
    except Exception as e:
        logger.error(f"创建 MultiMCPAgent 失败: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        return None
    
async def run_multimcp_agent(message: str, stream = False) -> str:
    server_configs = load_server_config()
    if not server_configs:
        logger.warning("没有有效的服务器配置，无法创建代理")
        return None

    commands = []
    urls = []
    urls_transports = []

    logger.info(f"Processing {len(server_configs)} server configurations: {[c['name'] for c in server_configs]}")
    for config in server_configs:
        try:
            name = config.get("name")
            command = config.get("command")
            args = config.get("args", [])
            timeout = config.get("timeout", 10)
            
            if not name or not command or not args:
                logger.error(f"Invalid configuration for server '{name}': {config}")
                continue

            if command == "sse" or command == "streamable-http":
                if not args[0].startswith("http"):
                    logger.error(f"Invalid SSE configuration for server '{name}': args must contain a valid HTTP URL")
                    continue
                urls.append(args[0])
                urls_transports.append(command)
                logger.info(f"Added SSE server: {name}, url: {args[0]}, urls_transports: {urls_transports}")
            else:
                commands.append(" ".join([command] + args))
                logger.info(f"Added Stdio server: {name}, command: {' '.join([command] + args)}")
        except Exception as e:
            logger.error(f"处理服务器配置失败，服务器 {name}: {str(e)}")
            logger.info(f"Stack trace: {traceback.format_exc()}")
            continue

    if not commands and not urls:
        logger.warning("没有有效的服务器配置可用于 MultiMCPTools")
        return None

    try:
        async with MultiMCPTools(
            commands=commands,
            urls=urls,
            urls_transports=urls_transports,
            timeout_seconds=int(max(config.get("timeout", 10) for config in server_configs))
        ) as mcp_tools:
            function_names = [getattr(f, 'name', key) for key, f in mcp_tools.functions.items()]
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
            logger.info(f"创建代理: {agent.name}，工具: {function_names}")
            run_response = await agent.arun(message=message,
                                    stream=stream,
                                    markdown=True,
                                    stream_intermediate_steps=True)
            response = ""
            async for run_response_chunk in run_response:
                run_response_chunk = cast(RunResponse, run_response_chunk)
                response += run_response_chunk.to_json()
            return response

    except Exception as e:
        logger.error(f"创建 MultiMCPAgent 失败: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        return None

async def run_multimcp_agent_stream(message: str, stream = False) -> str:
    server_configs = load_server_config()
    if not server_configs:
        logger.warning("没有有效的服务器配置，无法创建代理")
        return None

    commands = []
    urls = []
    urls_transports = []

    logger.info(f"Processing {len(server_configs)} server configurations: {[c['name'] for c in server_configs]}")
    for config in server_configs:
        try:
            name = config.get("name")
            command = config.get("command")
            args = config.get("args", [])
            timeout = config.get("timeout", 10)
            
            if not name or not command or not args:
                logger.error(f"Invalid configuration for server '{name}': {config}")
                continue

            if command == "sse" or command == "streamable-http":
                if not args[0].startswith("http"):
                    logger.error(f"Invalid SSE configuration for server '{name}': args must contain a valid HTTP URL")
                    continue
                urls.append(args[0])
                urls_transports.append(command)
                logger.info(f"Added SSE server: {name}, url: {args[0]}, urls_transports: {urls_transports}")
            else:
                commands.append(" ".join([command] + args))
                logger.info(f"Added Stdio server: {name}, command: {' '.join([command] + args)}")
        except Exception as e:
            logger.error(f"处理服务器配置失败，服务器 {name}: {str(e)}")
            logger.info(f"Stack trace: {traceback.format_exc()}")
            continue

    if not commands and not urls:
        logger.warning("没有有效的服务器配置可用于 MultiMCPTools")
        return None

    try:
        async with MultiMCPTools(
            commands=commands,
            urls=urls,
            urls_transports=urls_transports,
            timeout_seconds=int(max(config.get("timeout", 10) for config in server_configs))
        ) as mcp_tools:
            function_names = [getattr(f, 'name', key) for key, f in mcp_tools.functions.items()]
            agent = Agent(
                name="MultiMCPAgent",
                instructions="You are a database agent. Use the MCP tools to complete the user's queries.",
                tools=[mcp_tools],
                memory=Memory(),
                model=OpenAIChat(id="gpt-4o"),
                markdown=True,
                add_datetime_to_instructions=True,
            )
            logger.info(f"创建代理: {agent.name}，工具: {function_names}")
            run_response = await agent.arun(message=message,
                                    stream=stream,
                                    markdown=True,
                                    stream_intermediate_steps=True)
            # response = ""
            # async for run_response_chunk in run_response:
            #     run_response_chunk = cast(RunResponse, run_response_chunk)
            #     response += run_response_chunk.to_json()
            return run_response

    except Exception as e:
        logger.error(f"创建 MultiMCPAgent 失败: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        return None