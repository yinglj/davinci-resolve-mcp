# file: mcp_agents.py
import traceback
from typing import Optional, AsyncGenerator, cast
from agno.agent import Agent, RunResponse
from agno.tools.mcp import MultiMCPTools
from logger import logger
from configure import load_server_config, get_llm_config
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama
from common_utils import initialize_embedder_and_vector_db, initialize_knowledge_base

async def create_multi_agent(server_name: str = "Davinci_resolve") -> Optional[Agent]:
    """
    Create a MultiMCPAgent based on server configuration.

    Args:
        server_name (str): Name of the server to initialize the agent for.

    Returns:
        Optional[Agent]: The initialized agent or None if creation fails.
    """
    server_configs = load_server_config()
    if not server_configs:
        logger.warning("No valid server configurations found, cannot create agent")
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

            if command in ["sse", "streamable-http"]:
                if not args or not args[0].startswith("http"):
                    logger.error(f"Invalid SSE configuration for server '{name}': args must contain a valid HTTP URL")
                    continue
                urls.append(args[0])
                urls_transports.append(command)
                logger.info(f"Added SSE server: {name}, url: {args[0]}, transport: {command}")
            else:
                commands.append(" ".join([command] + args))
                logger.info(f"Added Stdio server: {name}, command: {' '.join([command] + args)}")
        except Exception as e:
            logger.error(f"Failed to process server configuration for {name}: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            continue

    if not commands and not urls:
        logger.warning("No valid server configurations available for MultiMCPTools")
        return None

    # Initialize embedder and vector database
    vector_db, embedder = initialize_embedder_and_vector_db(server_name)
    if not vector_db or not embedder:
        return None

    # Initialize knowledge base
    knowledge_base = initialize_knowledge_base(server_name, vector_db)

    # Determine LLM model based on preference
    try:
        llm_type, llm_model = get_llm_config(server_name)
        model = Ollama(id=llm_model) if llm_type == "ollama" else OpenAIChat(id=llm_model)
        logger.info(f"Using LLM model for {server_name}: type={llm_type}, model={llm_model}")
    except Exception as e:
        logger.error(f"Failed to load LLM configuration for {server_name}: {str(e)}")
        return None

    try:
        # Store tool configuration for runtime initialization
        tool_config = {
            "commands": commands,
            "urls": urls,
            "urls_transports": urls_transports,
            "timeout_seconds": int(max(config.get("timeout", 10) for config in server_configs)),
        }
        agent = Agent(
            name=f"MultiMCPAgent_{server_name}",
            instructions=f"You are a {server_name} agent. Use the MCP tools and knowledge base to complete the user's queries.",
            tools=[],  # Tools will be initialized at runtime
            model=model,
            markdown=True,
            add_datetime_to_instructions=True,
            show_tool_calls=True,
            knowledge=knowledge_base,
            search_knowledge=bool(knowledge_base),
        )
        setattr(agent, "_mcp_tool_config", tool_config)
        logger.info(f"Created agent: {agent.name}, tool config: {tool_config}")
        return agent
    except Exception as e:
        logger.error(f"Failed to create MultiMCPAgent for {server_name}: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        return None

async def run_multimcp_agent(message: str, server_name: str = "Davinci_resolve") -> dict | str:
    """
    Run the MultiMCPAgent for a given message in non-streaming mode.

    Args:
        message (str): The query or message to process.
        server_name (str): The name of the server configuration to use.

    Returns:
        dict | str: A single response string or error dictionary.
    """
    agent = await create_multi_agent(server_name)
    if not agent:
        logger.error(f"Failed to create agent for {server_name}")
        return {"error": "Failed to create agent"}

    try:
        tool_config = getattr(agent, "_mcp_tool_config", {})
        async with MultiMCPTools(
            commands=tool_config.get("commands", []),
            urls=tool_config.get("urls", []),
            urls_transports=tool_config.get("urls_transports", []),
            timeout_seconds=tool_config.get("timeout_seconds", 10),
        ) as mcp_tools:
            agent.tools = [mcp_tools]
            logger.info(f"Initialized MultiMCPTools for {server_name} with config: {tool_config}")
            run_response = await agent.arun(
                message=message,
                stream=False,
                markdown=True,
                stream_intermediate_steps=False
            )
            response = cast(RunResponse, run_response)
            if hasattr(response, 'error') and response.error:
                return {"error": response.error}
            return response.to_json()
    except Exception as e:
        logger.error(f"Failed to run MultiMCPAgent for {server_name}: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        return {"error": f"Agent execution failed: {str(e)}"}

async def run_multimcp_agent_stream(message: str, server_name: str = "Davinci_resolve") -> AsyncGenerator[RunResponse, None]:
    """
    Run the MultiMCPAgent for a given message in streaming mode.

    Args:
        message (str): The query or message to process.
        server_name (str): The name of the server configuration to use.

    Yields:
        RunResponse: Stream of responses from the agent.
    """
    agent = await create_multi_agent(server_name)
    if not agent:
        logger.error(f"Failed to create agent for {server_name}")
        yield RunResponse(error="Failed to create agent")
        return

    try:
        tool_config = getattr(agent, "_mcp_tool_config", {})
        async with MultiMCPTools(
            commands=tool_config.get("commands", []),
            urls=tool_config.get("urls", []),
            urls_transports=tool_config.get("urls_transports", []),
            timeout_seconds=tool_config.get("timeout_seconds", 10),
        ) as mcp_tools:
            agent.tools = [mcp_tools]
            logger.info(f"Initialized MultiMCPTools for {server_name} with config: {tool_config}")
            run_response = await agent.arun(
                message=message,
                stream=True,
                markdown=True,
                stream_intermediate_steps=True
            )
            async for chunk in run_response:
                chunk = cast(RunResponse, chunk)
                yield chunk
    except Exception as e:
        logger.error(f"Failed to run MultiMCPAgent for {server_name}: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        yield RunResponse(error=f"Agent execution failed: {str(e)}")