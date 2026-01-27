#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server - Project Properties Utilities
Re-exports from split submodules for backward compatibility.
"""

# Re-export all functions from submodules
from src.utils.properties.core import (
    PROJECT_PROPERTY_TYPES,
    get_all_project_properties,
    get_project_property,
    set_project_property,
    get_timeline_format_settings,
    set_timeline_format,
)

from src.utils.properties.settings import (
    get_superscale_settings,
    set_superscale_settings,
    get_color_settings,
    set_color_science_mode,
    set_color_space,
    get_project_metadata,
    get_project_info,
)

__all__ = [
    # Core
    "PROJECT_PROPERTY_TYPES",
    "get_all_project_properties",
    "get_project_property",
    "set_project_property",
    "get_timeline_format_settings",
    "set_timeline_format",
    # Settings
    "get_superscale_settings",
    "set_superscale_settings",
    "get_color_settings",
    "set_color_science_mode",
    "set_color_space",
    "get_project_metadata",
    "get_project_info",
]
