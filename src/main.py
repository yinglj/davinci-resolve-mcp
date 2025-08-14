#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server - Main Entry Point
This file serves as the main entry point for running the DaVinci Resolve MCP server
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import netifaces

# Add the parent directory to sys.path to ensure imports work
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

# Import the connection utils first to set environment variables
from src.utils.resolve_connection import check_environment_variables, set_default_environment_variables
from src.resolve_mcp_server import create_mcp_instance, register_mcp_resources
from src.utils.logger import logger
# Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[logging.StreamHandler()]
# )
# logger = logging.getLogger("davinci-resolve-mcp.main")

def check_setup():
    """Check if the environment is properly set up."""
    env_status = check_environment_variables()
    if not env_status["all_set"]:
        logger.warning(f"Setting default environment variables. Missing: {env_status['missing']}")
        set_default_environment_variables()
        
    return True

def get_all_ip_addresses():
    """Retrieve all non-loopback IP addresses."""
    try:
        # Get all network interfaces
        interfaces = netifaces.interfaces()
        ip_list = []
        
        # Iterate over each interface
        for interface in interfaces:
            # Get address information for the interface
            addrs = netifaces.ifaddresses(interface)
            # Check if IPv4 address (AF_INET) exists
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr.get('addr')
                    if ip and ip != '127.0.0.1':  # Exclude local loopback address
                        ip_list.append((interface, ip))
        
        return ip_list if ip_list else "No non-loopback IP addresses found"
    except Exception as e:
        return f"Failed to retrieve IP addresses: {e}"

def run_server(debug=False, port=8020, mode="streamable-http"):
    """Run the MCP server with the specified mode."""
    from src.resolve_mcp_server import create_mcp_instance
    
    # Set logging level based on debug flag
    if debug:
        logging.getLogger("davinci-resolve-mcp").setLevel(logging.DEBUG)
        logger.info("Debug mode enabled")
    
    # Validate mode
    valid_modes = ["stdio", "sse", "streamable-http"]
    if mode not in valid_modes:
        logger.error(f"Invalid mode: {mode}. Supported modes are: {', '.join(valid_modes)}")
        return 1
    
    # Create MCP instance
    try:
        mcp = create_mcp_instance(mode=mode, host="0.0.0.0", port=port)
        register_mcp_resources(mcp)
    except ValueError as e:
        logger.error(str(e))
        return 1
    
    # Run the server with the specified mode
    logger.print(f"Starting DaVinci Resolve MCP Server in {mode} mode...")
    # Log IP addresses for streamable-http mode
    if mode == "streamable-http":
        ip_list = get_all_ip_addresses()
        if isinstance(ip_list, str):
            logger.error(ip_list)
        else:
            for interface, ip in ip_list:
                logger.print(f"http://{ip}:{port}/mcp")
    
    mcp.run(transport=mode)
    return 0

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="DaVinci Resolve MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--port", type=int, default=8020, help="Port to run the server on (default: 8020)")
    parser.add_argument("--mode", type=str, default="streamable-http", 
                       choices=["stdio", "sse", "streamable-http"], 
                       help="Server transport mode (default: streamable-http)")
    args = parser.parse_args()
    logger.info(f"Arguments: {args}")
    
    if check_setup():
        return run_server(debug=args.debug, port=args.port, mode=args.mode)
    else:
        logger.error("Failed to set up the environment. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())