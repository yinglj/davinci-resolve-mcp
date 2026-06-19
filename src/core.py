#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server
A server that connects to DaVinci Resolve via the Model Context Protocol (MCP)

Version: 1.4.0 - Modular Architecture
"""

import os
import sys
import importlib
import logging

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import platform utilities
from .utils.platform import get_platform, get_resolve_paths

# Setup platform-specific paths and environment variables
paths = get_resolve_paths()
RESOLVE_API_PATH = paths["api_path"]
RESOLVE_LIB_PATH = paths["lib_path"]
RESOLVE_MODULES_PATH = paths["modules_path"]

os.environ["RESOLVE_SCRIPT_API"] = RESOLVE_API_PATH
os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_LIB_PATH

# Add the module path to Python's path if it's not already there
if RESOLVE_MODULES_PATH not in sys.path:
    sys.path.append(RESOLVE_MODULES_PATH)

# Import MCP
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("davinci-resolve-mcp")

# Log server version and platform
VERSION = "2.0.7"
logger.info(f"Starting DaVinci Resolve MCP Server v{VERSION}")
logger.info(f"Detected platform: {get_platform()}")
logger.info(f"Using Resolve API path: {RESOLVE_API_PATH}")
logger.info(f"Using Resolve library path: {RESOLVE_LIB_PATH}")

# Create MCP server instance
mcp = FastMCP("DaVinciResolveMCP", on_duplicate="ignore")


resolve_manager = importlib.import_module("src.utils.resolve_manager").resolve_manager


# Proxy class to allow tools to use 'resolve' dynamically
class ProxyResolve:
    """A proxy that always points to the current active Resolve instance."""

    @staticmethod
    def _null_method(*_args, **_kwargs):
        return None

    def _get_live_instance(self):
        instance = resolve_manager.instance

        if instance is None and resolve_manager.connect():
            instance = resolve_manager.instance

        if instance is None:
            return None

        project_manager_getter = getattr(instance, "GetProjectManager", None)
        project_manager = (
            project_manager_getter() if callable(project_manager_getter) else None
        )
        if project_manager is None and resolve_manager.connect():
            instance = resolve_manager.instance

        return instance

    def __getattr__(self, name):
        instance = self._get_live_instance()
        if instance is None:
            return self._null_method

        attr = getattr(instance, name, None)

        if callable(attr):

            def guarded_call(*args, **kwargs):
                live_instance = self._get_live_instance()
                if live_instance is None:
                    return None

                live_attr = getattr(live_instance, name, None)
                if not callable(live_attr):
                    if resolve_manager.connect():
                        live_instance = resolve_manager.instance
                        live_attr = (
                            getattr(live_instance, name, None)
                            if live_instance is not None
                            else None
                        )

                if not callable(live_attr):
                    return None

                return live_attr(*args, **kwargs)

            return guarded_call

        if attr is None and name and name[0].isupper():
            return self._null_method

        return attr

    def __bool__(self):
        return resolve_manager.is_connected()

    def __repr__(self):
        status = "Connected" if resolve_manager.is_connected() else "Disconnected"
        return f"<ProxyResolve: {status}>"


# Export 'resolve' as a proxy so tools capture the proxy, not the instance
resolve = ProxyResolve()


# Register all MCP tools
from .mcp_tools import register_all_tools
from .mcp_resources import register_all_resources
from .mcp_prompts import register_all_prompts
from .mcp_tasks import register_all_tasks

# Note: We pass the proxy 'resolve' to all registration functions
register_all_tools(mcp, resolve, logger)
logger.info("All MCP tools registered successfully")

# Register all MCP resources
register_all_resources(mcp, resolve, logger)
logger.info("All MCP resources registered successfully")

# Register all MCP prompts
register_all_prompts(mcp, resolve, logger)
logger.info("All MCP prompts registered successfully")

# Register all MCP tasks
try:
    register_all_tasks(mcp, resolve, logger)
    logger.info("All MCP tasks registered successfully")
except ImportError as e:
    logger.warning(f"Could not load MCP tasks: {e}")
except Exception as e:
    logger.warning(f"Error registering MCP tasks: {e}")

try:
    from .tools.register_tools import register_all_new_tools

    register_all_new_tools(mcp, resolve)
    logger.info(
        "Registered new modular tools (database, media storage, gallery, timeline, markers, capture)"
    )
except ImportError as e:
    logger.warning(f"Could not load modular tools: {e}")
except Exception as e:
    logger.warning(f"Error registering modular tools: {e}")

try:
    from .tools.keyboard import register_keyboard_tools

    register_keyboard_tools(mcp)
    logger.info("Registered keyboard simulation tools")
except ImportError as e:
    logger.warning(f"Could not load keyboard tools: {e}")
except Exception as e:
    logger.warning(f"Error registering keyboard tools: {e}")

# Note: Legacy resolve_mcp_server tools are NOT mounted here to avoid duplicates.
# All tools are now provided via the new modular system in register_all_new_tools().


# Note: This module should be imported, not run directly.
# Use src/__main__.py as the entry point.
