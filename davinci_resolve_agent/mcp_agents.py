# file: mcp_agents.py
import traceback
from typing import Optional, AsyncGenerator, cast
from agno.agent import Agent, RunResponse
from agno.tools.mcp import MultiMCPTools
from logger import logger
from configure import load_server_config, load_knowledge_config, load_embedder_config, get_llm_config
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama
from agno.knowledge.pdf_bytes import PDFBytesKnowledgeBase
from agno.embedder.ollama import OllamaEmbedder
from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb

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

    # Load embedder configuration
    try:
        embedder_type, embedder_model, dimensions = load_embedder_config(server_name)
        if embedder_type == "ollama":
            embedder = OllamaEmbedder(id=embedder_model, dimensions=dimensions)
        elif embedder_type == "openai":
            embedder = OpenAIEmbedder(model=embedder_model, dimensions=dimensions)
        else:
            logger.error(f"Unsupported embedder type {embedder_type}, defaulting to Ollama")
            embedder = OllamaEmbedder(id="hf.co/jinaai/jina-embeddings-v4-text-retrieval-GGUF:Q4_K_M", dimensions=2048)
    except Exception as e:
        logger.error(f"Failed to load embedder configuration for {server_name}: {str(e)}")
        return None

    # Load knowledge files
    knowledge_files = load_knowledge_config(server_name)
    knowledge_base = None
    if knowledge_files:
        knowledge_docs = []
        for file_path in knowledge_files:
            if file_path.endswith(('.pdf', '.PDF')):
                with open(file_path, "rb") as f:
                    knowledge_docs.append(f.read())
            elif file_path.endswith(('.md', '.txt')):
                with open(file_path, "r", encoding="utf-8") as f:
                    knowledge_docs.append(f.read())
            else:
                logger.warning(f"Unsupported file type: {file_path}")
        
        if knowledge_docs:
            try:
                vector_db = LanceDb(
                    table_name="knowledge_base",
                    uri="tmp/lancedb",
                    embedder=embedder,
                )
                knowledge_base = PDFBytesKnowledgeBase(
                    pdfs=[doc for doc in knowledge_docs if isinstance(doc, bytes)],
                    texts=[doc for doc in knowledge_docs if isinstance(doc, str)],
                    vector_db=vector_db,
                )
                await knowledge_base.aload(recreate=False)
                logger.info(f"Knowledge base loaded with {len(knowledge_docs)} documents for {server_name}")
            except Exception as e:
                logger.error(f"Failed to load knowledge base for {server_name}: {str(e)}")
                try:
                    await knowledge_base.aload(recreate=True)
                    logger.info(f"Knowledge base recreated and loaded successfully for {server_name}")
                except Exception as reinit_e:
                    logger.error(f"Knowledge base recreation failed: {str(reinit_e)}")
                    knowledge_base = None

    # Determine LLM model based on preference
    try:
        llm_type, llm_model = get_llm_config(server_name)
        model = (
            Ollama(id=llm_model) if llm_type == "ollama"
            else OpenAIChat(id=llm_model)
        )
        logger.info(f"Using LLM model for {server_name}: type={llm_type}, model={llm_model}")
    except Exception as e:
        logger.error(f"Failed to load LLM configuration for {server_name}: {str(e)}")
        return None

    try:
        # Create MultiMCPTools and Agent
        mcp_tools = MultiMCPTools(
            commands=commands,
            urls=urls,
            urls_transports=urls_transports,
            timeout_seconds=int(max(config.get("timeout", 10) for config in server_configs)),
        )
        function_names = [getattr(f, 'name', key) for key, f in mcp_tools.functions.items()]
        agent = Agent(
            name=f"MultiMCPAgent_{server_name}",
            instructions=f"You are a {server_name} agent. Use the MCP tools and knowledge base to complete the user's queries.",
            tools=[mcp_tools],
            model=model,
            markdown=True,
            add_datetime_to_instructions=True,
            show_tool_calls=True,
            knowledge=knowledge_base,
            search_knowledge=bool(knowledge_base),
        )
        logger.info(f"Created agent: {agent.name}, tools: {function_names}")
        return agent
    except Exception as e:
        logger.error(f"Failed to create MultiMCPAgent for {server_name}: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        return None

async def run_multimcp_agent(
    message: str,
    server_name: str = "Davinci_resolve"
) -> dict | str:
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
        run_response = await agent.arun(
            message=message,
            stream=False,
            markdown=True,
            stream_intermediate_steps=False
        )
        # Since stream=False, run_response should be a single RunResponse or similar
        response = cast(RunResponse, run_response)
        if hasattr(response, 'error') and response.error:
            return {"error": response.error}
        return response.to_json()
    except Exception as e:
        logger.error(f"Failed to run MultiMCPAgent for {server_name}: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        return {"error": f"Agent execution failed: {str(e)}"}

async def run_multimcp_agent_stream(
    message: str,
    server_name: str = "Davinci_resolve"
) -> AsyncGenerator[RunResponse, None]:
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