#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Layout related resources
"""

from typing import List, Dict, Any

from fastmcp.resources import ResourceContent, ResourceResult
from src.utils.layout_presets import list_layout_presets


def register_layout_resources(mcp, resolve, logger):
    """Register layout-related resources."""

    @mcp.resource("resolve://layout-presets")
    def get_layout_presets() -> ResourceResult:
        """Get all available layout presets for DaVinci Resolve."""
        if resolve is None:
            return ResourceResult(
                [ResourceContent({"error": "Not connected to DaVinci Resolve"})]
            )
        return ResourceResult([ResourceContent(list_layout_presets(layout_type="ui"))])

    logger.info("Layout resources registered")
