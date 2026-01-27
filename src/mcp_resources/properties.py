#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Property related resources
"""

from typing import Dict, Any
from src.utils.project_properties import (
    get_all_project_properties,
    get_project_property,
    get_timeline_format_settings,
    get_superscale_settings,
    get_color_settings,
    get_project_metadata,
    get_project_info,
)


def register_property_resources(mcp, resolve, logger):
    """Register property-related resources."""

    @mcp.resource("resolve://project/properties")
    def get_project_properties_endpoint() -> Dict[str, Any]:
        """Get all project properties for the current project."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return {"error": "No project currently open"}
        return get_all_project_properties(project)

    @mcp.resource("resolve://project/property/{property_name}")
    def get_project_property_endpoint(property_name: str) -> Dict[str, Any]:
        """Get a specific project property value."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return {"error": "No project currently open"}
        value = get_project_property(project, property_name)
        return {property_name: value}

    @mcp.resource("resolve://project/timeline-format")
    def get_timeline_format() -> Dict[str, Any]:
        """Get timeline format settings for the current project."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return {"error": "No project currently open"}
        return get_timeline_format_settings(project)

    @mcp.resource("resolve://project/superscale")
    def get_superscale_settings_endpoint() -> Dict[str, Any]:
        """Get SuperScale settings for the current project."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return {"error": "No project currently open"}
        return get_superscale_settings(project)

    @mcp.resource("resolve://project/color-settings")
    def get_color_settings_endpoint() -> Dict[str, Any]:
        """Get color science and color space settings for the current project."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return {"error": "No project currently open"}
        return get_color_settings(project)

    @mcp.resource("resolve://project/metadata")
    def get_project_metadata_endpoint() -> Dict[str, Any]:
        """Get metadata for the current project."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return {"error": "No project currently open"}
        return get_project_metadata(project)

    @mcp.resource("resolve://project/info")
    def get_project_info_endpoint() -> Dict[str, Any]:
        """Get comprehensive information about the current project."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return {"error": "No project currently open"}
        return get_project_info(project)

    logger.info("Property resources registered")
