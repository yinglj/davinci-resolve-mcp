#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Inspection related resources
"""

from typing import Any

from fastmcp.resources import ResourceContent, ResourceResult
from src.utils.object_inspection import inspect_object


def register_inspection_resources(mcp, resolve, logger):
    """Register inspection-related resources."""

    def to_resource_result(payload: Any) -> ResourceResult:
        return ResourceResult([ResourceContent(payload)])

    @mcp.resource("resolve://inspect/resolve")
    def inspect_resolve_object() -> ResourceResult:
        """Inspect the main resolve object."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        return to_resource_result(inspect_object(resolve))

    @mcp.resource("resolve://inspect/project-manager")
    def inspect_project_manager_object() -> ResourceResult:
        """Inspect the project manager object."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        pm = resolve.GetProjectManager()
        if not pm:
            return to_resource_result({"error": "Failed to get Project Manager"})
        return to_resource_result(inspect_object(pm))

    @mcp.resource("resolve://inspect/current-project")
    def inspect_current_project_object() -> ResourceResult:
        """Inspect the current project object."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        pm = resolve.GetProjectManager()
        if not pm:
            return to_resource_result({"error": "Failed to get Project Manager"})
        project = pm.GetCurrentProject()
        if not project:
            return to_resource_result({"error": "No project currently open"})
        return to_resource_result(inspect_object(project))

    @mcp.resource("resolve://inspect/media-pool")
    def inspect_media_pool_object() -> ResourceResult:
        """Inspect the media pool object."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        pm = resolve.GetProjectManager()
        if not pm:
            return to_resource_result({"error": "Failed to get Project Manager"})
        project = pm.GetCurrentProject()
        if not project:
            return to_resource_result({"error": "No project currently open"})
        mp = project.GetMediaPool()
        if not mp:
            return to_resource_result({"error": "Failed to get Media Pool"})
        return to_resource_result(inspect_object(mp))

    @mcp.resource("resolve://inspect/current-timeline")
    def inspect_current_timeline_object() -> ResourceResult:
        """Inspect the current timeline object."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})
        pm = resolve.GetProjectManager()
        if not pm:
            return to_resource_result({"error": "Failed to get Project Manager"})
        project = pm.GetCurrentProject()
        if not project:
            return to_resource_result({"error": "No project currently open"})
        timeline = project.GetCurrentTimeline()
        if not timeline:
            return to_resource_result({"error": "No timeline currently active"})
        return to_resource_result(inspect_object(timeline))

    logger.info("Inspection resources registered")
