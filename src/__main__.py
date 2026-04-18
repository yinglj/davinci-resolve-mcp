#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server - Main Entry Point
This file serves as the main entry point for running the DaVinci Resolve MCP server
Version: 1.4.0 - Modular Architecture with Streamable HTTP support
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Literal, cast

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Add the parent directory to sys.path to ensure imports work
# This allows us to import src_1.4.0 components as a package
project_dir = Path(__file__).parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

# Import the connection utils first to set environment variables
# Note: we use absolute imports relative to project_dir to avoid confusion
try:
    from src.utils.resolve_connection import (
        check_environment_variables,
        set_default_environment_variables,
    )
    from src.utils.network import get_all_ip_addresses
    from src.utils.logger import logger
except ModuleNotFoundError as e:
    if e.name not in {"src", "src.utils", "src.utils.resolve_connection", "src.utils.network", "src.utils.logger"}:
        raise
    # Fallback for if we're inside the package
    from .utils.resolve_connection import (
        check_environment_variables,
        set_default_environment_variables,
    )
    from .utils.network import get_all_ip_addresses
    from .utils.logger import logger

# Remove manual basicConfig as CustomLogger handles it


def build_http_middleware() -> list[Middleware]:
    """Add CORS support so browser-based MCP clients can complete preflight."""
    return [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id", "mcp-protocol-version"],
        )
    ]


def check_setup():
    """Check if the environment is properly set up."""
    env_status = check_environment_variables()
    if not env_status["all_set"]:
        logger.warning(
            f"Setting default environment variables. Missing: {env_status['missing']}"
        )
        set_default_environment_variables()

    return True


def run_server(
    debug: bool = False,
    port: int = 8020,
    mode: Literal["stdio", "sse", "streamable-http"] = "stdio",
):
    """Run the MCP server."""
    try:
        from src.core import mcp, resolve
    except ModuleNotFoundError as e:
        if e.name not in {"src", "src.core"}:
            raise
        from .core import mcp, resolve

    # Set logging level based on debug flag
    if debug:
        logging.getLogger("davinci-resolve-mcp").setLevel(logging.DEBUG)
        logger.print("Debug mode enabled")

    # Run the server
    logger.print(f"Starting DaVinci Resolve MCP Server in {mode} mode...")

    # Log IP addresses for streamable-http mode
    if mode == "streamable-http":
        ip_list = get_all_ip_addresses()
        if not ip_list:
            logger.error("No non-loopback IP addresses found")
        else:
            for interface, ip in ip_list:
                logger.print(f"http://{ip}:{port}/mcp")

    transport = "http" if mode == "streamable-http" else mode
    if transport == "stdio":
        mcp.run(transport=transport)
    else:
        mcp.run(
            transport=transport,
            host="0.0.0.0",
            port=port,
            middleware=build_http_middleware(),
        )


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="DaVinci Resolve MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--port",
        type=int,
        default=8020,
        help="Port to run the server on (default: 8020)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="streamable-http",
        choices=["stdio", "sse", "streamable-http"],
        help="Server transport mode (default: streamable-http)",
    )
    args = parser.parse_args()

    if check_setup():
        mode = cast(Literal["stdio", "sse", "streamable-http"], args.mode)
        run_server(debug=args.debug, port=args.port, mode=mode)
    else:
        logger.error(
            "Failed to set up the environment. Please check the configuration."
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
