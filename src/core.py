#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server
A server that connects to DaVinci Resolve via the Model Context Protocol (MCP)

Version: 1.4.0 - Modular Architecture
"""

import os
import sys
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
VERSION = "1.4.0"
logger.info(f"Starting DaVinci Resolve MCP Server v{VERSION}")
logger.info(f"Detected platform: {get_platform()}")
logger.info(f"Using Resolve API path: {RESOLVE_API_PATH}")
logger.info(f"Using Resolve library path: {RESOLVE_LIB_PATH}")

# Create MCP server instance
mcp = FastMCP("DaVinciResolveMCP")


# Create Resolve connection manager
class ResolveConnection:
    def __init__(self):
        self._resolve = None
        self.logger = logger

    def connect(self):
        """Initialize or refresh the connection to DaVinci Resolve."""
        try:
            # Ensure environment variables are set
            from .utils.resolve_connection import set_default_environment_variables

            set_default_environment_variables()

            import DaVinciResolveScript as dvr_script

            self._resolve = dvr_script.scriptapp("Resolve")

            if self._resolve:
                self.logger.info(
                    f"Successfully connected to DaVinci Resolve: {self._resolve.GetProductName()} {self._resolve.GetVersionString()}"
                )
                return True
            else:
                self.logger.warning(
                    "DaVinci Resolve is not running or scripting is not enabled."
                )
                return False
        except ImportError as e:
            self.logger.error(
                f"Failed to import DaVinciResolveScript (PYTHONPATH may be incorrect): {e}"
            )
            return False
        except Exception as e:
            self.logger.error(f"Error connecting to DaVinci Resolve: {e}")
            return False

    @property
    def instance(self):
        """Get the current Resolve instance."""
        return self._resolve

    def is_connected(self):
        """Check if we are currently connected."""
        return self._resolve is not None


# Proxy class to allow tools to use 'resolve' dynamically
class ProxyResolve:
    """A proxy that always points to the current active Resolve instance."""

    def __getattr__(self, name):
        instance = resolve_manager.instance
        if instance is None:
            # Attempt one silent reconnect if being accessed
            if resolve_manager.connect():
                instance = resolve_manager.instance

        if instance is None:
            raise RuntimeError(
                "Not connected to DaVinci Resolve. Please ensure Resolve is running and call 'reconnect_resolve' tool."
            )

        return getattr(instance, name)

    def __bool__(self):
        return resolve_manager.is_connected()

    def __repr__(self):
        status = "Connected" if resolve_manager.is_connected() else "Disconnected"
        return f"<ProxyResolve: {status}>"


# Initialize connection manager
resolve_manager = ResolveConnection()
resolve_manager.connect()

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
register_all_tasks(mcp, resolve, logger)
logger.info("All MCP tasks registered successfully")


# Note: This module should be imported, not run directly.
# Use src/__main__.py as the entry point.
