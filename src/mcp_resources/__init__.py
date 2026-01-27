#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Registration Module
"""

from .project import register_project_resources
from .timeline import register_timeline_resources
from .media import register_media_resources
from .app import register_app_resources
from .color import register_color_resources
from .delivery import register_delivery_resources
from .inspection import register_inspection_resources
from .properties import register_property_resources
from .layout import register_layout_resources
from .presets import register_preset_resources
from .cache import register_cache_resources
from .timeline_items import register_timeline_item_resources
from .cloud import register_cloud_resources
from .keyframes import register_keyframe_resources


def register_all_resources(mcp, resolve, logger):
    """Register all MCP resources."""
    register_project_resources(mcp, resolve, logger)
    register_timeline_resources(mcp, resolve, logger)
    register_media_resources(mcp, resolve, logger)
    register_app_resources(mcp, resolve, logger)
    register_color_resources(mcp, resolve, logger)
    register_delivery_resources(mcp, resolve, logger)
    register_inspection_resources(mcp, resolve, logger)
    register_property_resources(mcp, resolve, logger)
    register_layout_resources(mcp, resolve, logger)
    register_preset_resources(mcp, resolve, logger)
    register_cache_resources(mcp, resolve, logger)
    register_timeline_item_resources(mcp, resolve, logger)
    register_cloud_resources(mcp, resolve, logger)
    register_keyframe_resources(mcp, resolve, logger)


__all__ = ["register_all_resources"]
