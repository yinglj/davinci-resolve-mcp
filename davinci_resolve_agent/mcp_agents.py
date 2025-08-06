# file: mcp_agents.py
import traceback
from typing import Optional, AsyncGenerator, cast
from pathlib import Path
from agno.agent import Agent, RunResponse
from agno.tools.mcp import MultiMCPTools
from logger import logger
from configure import load_server_config, load_knowledge_config, load_embedder_config, get_llm_config
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama
from agno.knowledge.pdf_bytes import PDFBytesKnowledgeBase
from agno.knowledge.markdown import MarkdownKnowledgeBase
from agno.knowledge.csv import CSVKnowledgeBase
from agno.knowledge.text import TextKnowledgeBase
from agno.knowledge.combined import CombinedKnowledgeBase
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

    # Initialize vector database
    vector_db = LanceDb(
        table_name="knowledge_base",
        uri="tmp/lancedb",
        embedder=embedder,
    )

    # Load knowledge files
    knowledge_files = load_knowledge_config(server_name)
    knowledge_base = None
    if knowledge_files:
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
            elif file_path.endswith('.txt'):
                text_files.append({"path": file_path, "metadata": metadata})
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
                    logger.warning(f"File type isn't supported: {file_path}")
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
                    vector_db=vector_db,
                )
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
                    num_documents=5,  # Number of documents to return on search
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

        # Combine knowledge bases
        if knowledge_bases:
            try:
                knowledge_base = CombinedKnowledgeBase(
                    sources=knowledge_bases,
                    vector_db=vector_db,
                )
                await knowledge_base.aload(recreate=False)
                logger.info(f"Combined knowledge base loaded with {len(knowledge_bases)} sources for {server_name}")
            except Exception as e:
                logger.error(f"Failed to load combined knowledge base for {server_name}: {str(e)}")
                try:
                    await knowledge_base.aload(recreate=True)
                    logger.info(f"Combined knowledge base recreated and loaded successfully for {server_name}")
                except Exception as reinit_e:
                    logger.error(f"Combined knowledge base recreation failed: {str(reinit_e)}")
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
        # Attach tool configuration to agent for runtime use
        setattr(agent, "_mcp_tool_config", tool_config)
        logger.info(f"Created agent: {agent.name}, tool config: {tool_config}")
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
        # Initialize MultiMCPTools at runtime
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
        # Initialize MultiMCPTools at runtime
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