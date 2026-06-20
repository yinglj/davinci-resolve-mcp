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
    # Unique tools only - duplicate granular tools are skipped to prefer upstream
    register_core_tools(mcp, resolve, logger)  # reconnect_resolve only (unique)
    register_color_tools(mcp, resolve, logger)  # color_group, graph (unique); skip add_node, apply_lut, copy_grade, set_color_wheel_param (dups)
    register_media_tools(mcp, resolve, logger)  # overwrite_clip, append_to_timeline (unique); skip 10 dups
    register_render_presets_tools(mcp, resolve, logger)  # render_presets (unique)
    register_timeline_ai_tools(mcp, resolve, logger)  # timeline_ai (unique)
    register_gallery_stills_tools(mcp, resolve, logger)  # gallery_stills (unique)
    register_project_manager_folders_tools(mcp, resolve, logger)  # project_manager_folders (unique)
    register_project_manager_database_tools(mcp, resolve, logger)  # project_manager_database (unique)
    register_media_pool_item_markers_tools(mcp, resolve, logger)  # media_pool_item_markers (unique)
    register_timeline_item_markers_tools(mcp, resolve, logger)  # timeline_item_markers (unique)
    # Skipped - all tools are duplicates of granular (prefer granular):
    # register_project_tools (5 dups: close_project, create_project, open_project, save_project, set_project_setting)
    # register_timeline_tools (6 dups: add_marker, create_empty_timeline, create_timeline, delete_timeline, list_timelines_tool, set_current_timeline)
    # register_delivery_tools (8 dups: add_to_render_queue, clear_render_queue, clear_transcription, link_proxy_media, replace_clip, start_render, transcribe_audio, unlink_proxy_media)
    # register_cache_tools (10 dups: clear_folder_transcription, delete_optimized_media, export_folder, generate_optimized_media, set_cache_mode, set_cache_path, set_optimized_media_mode, set_proxy_mode, set_proxy_quality, transcribe_folder_audio)
    # register_timeline_item_tools (5 dups: add_keyframe, delete_keyframe, enable_keyframes, modify_keyframe, set_keyframe_interpolation)
    # register_preset_tools (6 dups: delete_layout_preset_tool, export_layout_preset_tool, import_layout_preset_tool, load_layout_preset_tool, save_layout_preset_tool, set_color_wheel_param)
    # register_inspection_tools (2 dups: inspect_custom_object, object_help)
    # register_layout_tools (5 dups)
    # register_app_tools (4 dups: open_app_preferences, open_settings, quit_app, restart_app)
    # register_cloud_tools (6 dups)
    # register_property_tools (5 dups)


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
