#!/usr/bin/env python3
"""
DaVinci Resolve MCP Tools - Split Module
Provides registration functions for all MCP tools and resources.
"""

from .core import register_core_tools
from .project import register_project_tools
from .timeline import register_timeline_tools
from .media import register_media_tools
from .color import register_color_tools
from .delivery import register_delivery_tools
from .cache import register_cache_tools
from .timeline_items import register_timeline_item_tools
from .keyframes import register_keyframe_tools
from .presets import register_preset_tools
from .render_presets import register_render_presets_tools
from .inspection import register_inspection_tools
from .layout import register_layout_tools
from .app import register_app_tools
from .cloud import register_cloud_tools
from .properties import register_property_tools
from .timeline_ai import register_timeline_ai_tools
from .gallery_stills import register_gallery_stills_tools
from .project_manager_folders import register_project_manager_folders_tools
from .project_manager_database import register_project_manager_database_tools
from .media_pool_item_markers import register_media_pool_item_markers_tools
from .timeline_item_markers import register_timeline_item_markers_tools


def register_all_tools(mcp, resolve, logger):
    """Register all MCP tools and resources."""
    register_core_tools(mcp, resolve, logger)
    register_project_tools(mcp, resolve, logger)
    register_timeline_tools(mcp, resolve, logger)
    register_media_tools(mcp, resolve, logger)
    register_color_tools(mcp, resolve, logger)
    register_delivery_tools(mcp, resolve, logger)
    register_cache_tools(mcp, resolve, logger)
    register_timeline_item_tools(mcp, resolve, logger)
    register_keyframe_tools(mcp, resolve, logger)
    register_preset_tools(mcp, resolve, logger)
    register_render_presets_tools(mcp, resolve, logger)
    register_inspection_tools(mcp, resolve, logger)
    register_layout_tools(mcp, resolve, logger)
    register_app_tools(mcp, resolve, logger)
    register_cloud_tools(mcp, resolve, logger)
    register_property_tools(mcp, resolve, logger)
    register_timeline_ai_tools(mcp, resolve, logger)
    register_gallery_stills_tools(mcp, resolve, logger)
    register_project_manager_folders_tools(mcp, resolve, logger)
    register_project_manager_database_tools(mcp, resolve, logger)
    register_media_pool_item_markers_tools(mcp, resolve, logger)
    register_timeline_item_markers_tools(mcp, resolve, logger)


__all__ = [
    "register_all_tools",
    "register_core_tools",
    "register_project_tools",
    "register_timeline_tools",
    "register_media_tools",
    "register_color_tools",
    "register_delivery_tools",
    "register_cache_tools",
    "register_timeline_item_tools",
    "register_keyframe_tools",
    "register_preset_tools",
    "register_render_presets_tools",
    "register_inspection_tools",
    "register_layout_tools",
    "register_app_tools",
    "register_cloud_tools",
    "register_property_tools",
    "register_timeline_ai_tools",
    "register_gallery_stills_tools",
    "register_project_manager_folders_tools",
    "register_project_manager_database_tools",
    "register_media_pool_item_markers_tools",
    "register_timeline_item_markers_tools",
]
