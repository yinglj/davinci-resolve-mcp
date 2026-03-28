#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Color related resources
"""

from typing import Any, Optional

from fastmcp.resources import ResourceContent, ResourceResult


def register_color_resources(mcp, resolve, logger):
    """Register color-related resources."""

    def to_resource_result(payload: Any) -> ResourceResult:
        return ResourceResult([ResourceContent(payload)])

    @mcp.resource("resolve://color/current-node")
    def get_current_color_node() -> ResourceResult:
        """Get information about the current node in the color page."""
        try:
            from src.api.color import get_current_node as get_node_func
        except ImportError:
            return to_resource_result({"error": "Could not import color operations"})

        return to_resource_result(get_node_func(resolve))

    @mcp.resource("resolve://color/wheels/{node_index}")
    def get_color_wheel_params(
        node_index: Optional[int] = None,
    ) -> ResourceResult:
        """Get the current color wheel parameters for a specified node."""
        try:
            from src.api.color import get_color_wheels as get_wheels_func
        except ImportError:
            return to_resource_result({"error": "Could not import color operations"})

        if node_index is None:
            return to_resource_result(get_wheels_func(resolve))
        return to_resource_result(get_wheels_func(resolve, node_index))

    logger.info("Color resources registered")
