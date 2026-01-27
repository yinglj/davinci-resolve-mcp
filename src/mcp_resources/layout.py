#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Layout related resources
"""

from typing import List, Dict, Any
from src.utils.layout_presets import list_layout_presets


def register_layout_resources(mcp, resolve, logger):
    """Register layout-related resources."""

    @mcp.resource("resolve://layout-presets")
    def get_layout_presets() -> List[Dict[str, Any]]:
        """Get all available layout presets for DaVinci Resolve."""
        if resolve is None:
            return [{"error": "Not connected to DaVinci Resolve"}]
        return list_layout_presets(layout_type="ui")

    logger.info("Layout resources registered")
