# file: configure.py
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from logger import logger

class ConfigError(Exception):
    pass

def _load_config(config_path: str = "mcp_config.json") -> Optional[Dict[str, Any]]:
    if not os.path.exists(config_path):
        logger.error(f"Configuration file {config_path} not found")
        return None
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        if not isinstance(config, dict):
            logger.error(f"Invalid configuration format in {config_path}: expected a dict")
            return None
        return config
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {config_path}: {str(e)}")
        return None
    except Exception as e:
        logger.exception(f"Error loading configuration from {config_path}")
        return None

def load_environment() -> None:
    pass

def load_server_config() -> List[Dict[str, Any]]:
    config = _load_config()
    if config is None:
        return []
    mcp_servers = config.get("mcpServers")
    if not isinstance(mcp_servers, dict):
        logger.error(f"Invalid mcpServers format: expected a dict, got {type(mcp_servers)}")
        return []
    servers = []
    mcp_prompts_enhancement_server = None
    for name, server_config in mcp_servers.items():
        if not isinstance(server_config, dict):
            logger.error(f"Invalid server configuration for {name}: expected a dict, got {type(server_config)}")
            continue
        server_entry = server_config.copy()
        server_entry["name"] = name
        if "timeout" in server_entry:
            timeout = server_entry["timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                logger.warning(f"Invalid timeout value for server {name}: {timeout}, ignoring")
                del server_entry["timeout"]
        if name == "mcp_prompts_enhancement":
            mcp_prompts_enhancement_server = server_entry
        else:
            servers.append(server_entry)
    if mcp_prompts_enhancement_server:
        servers.append(mcp_prompts_enhancement_server)
    if not servers:
        logger.error("No valid server configurations found")
        return []
    return servers

def load_api_keys() -> Dict[str, str]:
    config = _load_config()
    if config is None:
        return {}
    api_keys = config.get("apiKeys", {})
    if not isinstance(api_keys, dict):
        logger.error(f"Invalid apiKeys format: expected a dict, got {type(api_keys)}")
        return {}
    for key, user in api_keys.items():
        if not isinstance(key, str) or not isinstance(user, str):
            logger.error(f"Invalid apiKeys entry: key '{key}' or value '{user}' is not a string")
            return {}
    if not api_keys:
        logger.warning("No API keys found")
    return api_keys

def load_timeout() -> float:
    default_timeout = 10.0
    config = _load_config()
    if config is None:
        logger.info(f"Using default timeout: {default_timeout} seconds")
        return default_timeout
    timeout = config.get("timeout", default_timeout)
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        logger.warning(f"Invalid timeout value in config: {timeout}, using default: {default_timeout}")
        return default_timeout
    logger.info(f"Loaded timeout from config: {timeout} seconds")
    return float(timeout)

def load_server_timeout(server_name: str) -> float:
    default_timeout = 10.0
    config = _load_config()
    if config is None:
        logger.debug(f"Using default timeout for server {server_name}: {default_timeout} seconds")
        return default_timeout
    mcp_servers = config.get("mcpServers", {})
    server_config = mcp_servers.get(server_name, {})
    timeout = server_config.get("timeout", default_timeout)
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        logger.warning(f"Invalid timeout value for server {server_name}: {timeout}, using default: {default_timeout}")
        return default_timeout
    logger.debug(f"Loaded timeout for server {server_name}: {timeout} seconds")
    return float(timeout)

def get_llm_preference() -> str:
    default_preference = "openai"
    config = _load_config()
    if config is None:
        logger.info(f"Using default LLM preference: {default_preference}")
        return default_preference
    llm_preference = config.get("llm_preference", default_preference)
    if not isinstance(llm_preference, str) or not llm_preference:
        logger.warning(f"Invalid llm_preference value in config: {llm_preference}, using default: {default_preference}")
        return default_preference
    logger.info(f"Loaded LLM preference from config: {llm_preference}")
    return llm_preference

def load_knowledge_config(server_name: str = None, config_path: str = "mcp_config.json") -> List[str]:
    """
    Load knowledge files from mcp_config.json, optionally filtered by server name.

    Args:
        server_name (str, optional): The name of the server to load knowledge files for.
        config_path (str): Path to the configuration file.

    Returns:
        List[str]: List of valid file paths.
    """
    if not os.path.exists(config_path):
        logger.error(f"Knowledge configuration file {config_path} not found")
        return []
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        knowledge_files = []
        if server_name:
            mcp_servers = config.get("mcpServers", {})
            server_config = mcp_servers.get(server_name, {})
            knowledge_files = server_config.get("knowledgeFiles", [])
        else:
            knowledge_files = config.get("knowledgeFiles", [])
        if not isinstance(knowledge_files, list):
            logger.error(f"Invalid knowledgeFiles format in {config_path}: expected a list, got {type(knowledge_files)}")
            return []
        valid_files = []
        base_dir = os.path.dirname(config_path)
        for file_path in knowledge_files:
            full_path = os.path.join(base_dir, file_path)
            if os.path.exists(full_path):
                valid_files.append(full_path)
            else:
                logger.warning(f"Knowledge file not found: {full_path}")
        if not valid_files:
            logger.warning(f"No valid knowledge files found in {config_path} for server {server_name or 'global'}")
        return valid_files
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {config_path}: {str(e)}")
        return []
    except Exception as e:
        logger.exception(f"Error loading knowledge configuration from {config_path}")
        return []

def load_embedder_config(server_name: str, config_path: str = "mcp_config.json") -> Tuple[str, str, int]:
    """
    Load embedder configuration from mcp_config.json for a specific server.

    Args:
        server_name (str): The name of the server to load embedder config for.
        config_path (str): Path to the configuration file.

    Returns:
        Tuple[str, str, int]: Tuple of (type, model, dimensions) for the embedder.

    Raises:
        ConfigError: If embedder configuration is invalid or missing.
    """
    config = _load_config(config_path)
    if config is None:
        logger.error(f"Failed to load config for embedder of server {server_name}")
        raise ConfigError("Configuration file not found or invalid")
    
    mcp_servers = config.get("mcpServers", {})
    server_config = mcp_servers.get(server_name, {})
    embedder_config = server_config.get("embedder", {})
    
    if not isinstance(embedder_config, dict):
        logger.error(f"Invalid embedder configuration for server {server_name}: expected a dict, got {type(embedder_config)}")
        raise ConfigError(f"Invalid embedder configuration for server {server_name}")
    
    embedder_type = embedder_config.get("type", "ollama")  # Default to ollama
    embedder_model = embedder_config.get("model", "hf.co/jinaai/jina-embeddings-v4-text-retrieval-GGUF:Q4_K_M")
    dimensions = embedder_config.get("dimensions", 2048)
    
    if not isinstance(embedder_type, str) or embedder_type not in ["ollama", "openai"]:
        logger.error(f"Invalid embedder type for server {server_name}: {embedder_type}, using default 'ollama'")
        embedder_type = "ollama"
    if not isinstance(embedder_model, str) or not embedder_model:
        logger.error(f"Invalid embedder model for server {server_name}: {embedder_model}")
        raise ConfigError(f"Invalid embedder model for server {server_name}")
    if not isinstance(dimensions, int) or dimensions <= 0:
        logger.error(f"Invalid embedder dimensions for server {server_name}: {dimensions}")
        raise ConfigError(f"Invalid embedder dimensions for server {server_name}")
    
    logger.info(f"Loaded embedder config for server {server_name}: type={embedder_type}, model={embedder_model}, dimensions={dimensions}")
    return embedder_type, embedder_model, dimensions