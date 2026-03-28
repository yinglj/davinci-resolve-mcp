#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Property related resources
"""

from typing import Any

from fastmcp.resources import ResourceContent, ResourceResult
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

    def to_resource_result(payload: Any) -> ResourceResult:
        return ResourceResult([ResourceContent(payload)])

    @mcp.resource("resolve://project/properties")
    def get_project_properties_endpoint() -> ResourceResult:
        """Get all project properties for the current project."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return to_resource_result({"error": "No project currently open"})
        return to_resource_result(get_all_project_properties(project))

    @mcp.resource("resolve://project/property/{property_name}")
    def get_project_property_endpoint(property_name: str) -> ResourceResult:
        """Get a specific project property value."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return to_resource_result({"error": "No project currently open"})
        value = get_project_property(project, property_name)
        return to_resource_result({property_name: value})

    @mcp.resource("resolve://project/timeline-format")
    def get_timeline_format() -> ResourceResult:
        """Get timeline format settings for the current project."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return to_resource_result({"error": "No project currently open"})
        return to_resource_result(get_timeline_format_settings(project))

    @mcp.resource("resolve://project/superscale")
    def get_superscale_settings_endpoint() -> ResourceResult:
        """Get SuperScale settings for the current project."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return to_resource_result({"error": "No project currently open"})
        return to_resource_result(get_superscale_settings(project))

    @mcp.resource("resolve://project/color-settings")
    def get_color_settings_endpoint() -> ResourceResult:
        """Get color science and color space settings for the current project."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return to_resource_result({"error": "No project currently open"})
        return to_resource_result(get_color_settings(project))

    @mcp.resource("resolve://project/metadata")
    def get_project_metadata_endpoint() -> ResourceResult:
        """Get metadata for the current project."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return to_resource_result({"error": "No project currently open"})
        return to_resource_result(get_project_metadata(project))

    @mcp.resource("resolve://project/info")
    def get_project_info_endpoint() -> ResourceResult:
        """Get comprehensive information about the current project."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        if not project:
            return to_resource_result({"error": "No project currently open"})
        return to_resource_result(get_project_info(project))

    logger.info("Property resources registered")
