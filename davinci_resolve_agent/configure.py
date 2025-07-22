# file: configure.py
import json
import os
from typing import List, Dict, Any, Optional
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