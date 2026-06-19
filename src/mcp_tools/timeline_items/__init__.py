#!/usr/bin/env python3
"""
DaVinci Resolve MCP Timeline Item Tools
Timeline item properties and manipulation
"""

from .properties import register_timeline_item_property_tools
from .transforms import register_timeline_item_transform_tools
from .fusion import register_timeline_item_fusion_tools
from .color import register_timeline_item_color_tools
from .takes import register_timeline_item_takes_tools


def register_timeline_item_tools(mcp, resolve, logger):
    """Register all timeline item MCP tools and resources."""
    register_timeline_item_property_tools(mcp, resolve, logger)
    register_timeline_item_transform_tools(mcp, resolve, logger)
    register_timeline_item_fusion_tools(mcp, resolve, logger)
    register_timeline_item_color_tools(mcp, resolve, logger)
    register_timeline_item_takes_tools(mcp, resolve, logger)
    logger.info("Registered timeline item tools")
