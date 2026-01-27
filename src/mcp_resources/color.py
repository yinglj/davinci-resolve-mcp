#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Color related resources
"""

from typing import Dict, Any


def register_color_resources(mcp, resolve, logger):
    """Register color-related resources."""

    @mcp.resource("resolve://color/current-node")
    def get_current_color_node() -> Dict[str, Any]:
        """Get information about the current node in the color page."""
        try:
            from src.api.color_operations import get_current_node as get_node_func
        except ImportError:
            return {"error": "Could not import color operations"}

        return get_node_func(resolve)

    @mcp.resource("resolve://color/wheels/{node_index}")
    def get_color_wheel_params(node_index: int = None) -> Dict[str, Any]:
        """Get the current color wheel parameters for a specified node."""
        try:
            from src.api.color_operations import get_color_wheels as get_wheels_func
        except ImportError:
            return {"error": "Could not import color operations"}

        return get_wheels_func(resolve, node_index)

    logger.info("Color resources registered")
