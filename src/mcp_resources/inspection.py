#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Inspection related resources
"""

from typing import Dict, Any
from src.utils.object_inspection import inspect_object


def register_inspection_resources(mcp, resolve, logger):
    """Register inspection-related resources."""

    @mcp.resource("resolve://inspect/resolve")
    def inspect_resolve_object() -> Dict[str, Any]:
        """Inspect the main resolve object."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        return inspect_object(resolve)

    @mcp.resource("resolve://inspect/project-manager")
    def inspect_project_manager_object() -> Dict[str, Any]:
        """Inspect the project manager object."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        pm = resolve.GetProjectManager()
        if not pm:
            return {"error": "Failed to get Project Manager"}
        return inspect_object(pm)

    @mcp.resource("resolve://inspect/current-project")
    def inspect_current_project_object() -> Dict[str, Any]:
        """Inspect the current project object."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        pm = resolve.GetProjectManager()
        if not pm:
            return {"error": "Failed to get Project Manager"}
        project = pm.GetCurrentProject()
        if not project:
            return {"error": "No project currently open"}
        return inspect_object(project)

    @mcp.resource("resolve://inspect/media-pool")
    def inspect_media_pool_object() -> Dict[str, Any]:
        """Inspect the media pool object."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        pm = resolve.GetProjectManager()
        if not pm:
            return {"error": "Failed to get Project Manager"}
        project = pm.GetCurrentProject()
        if not project:
            return {"error": "No project currently open"}
        mp = project.GetMediaPool()
        if not mp:
            return {"error": "Failed to get Media Pool"}
        return inspect_object(mp)

    @mcp.resource("resolve://inspect/current-timeline")
    def inspect_current_timeline_object() -> Dict[str, Any]:
        """Inspect the current timeline object."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        pm = resolve.GetProjectManager()
        if not pm:
            return {"error": "Failed to get Project Manager"}
        project = pm.GetCurrentProject()
        if not project:
            return {"error": "No project currently open"}
        timeline = project.GetCurrentTimeline()
        if not timeline:
            return {"error": "No timeline currently active"}
        return inspect_object(timeline)

    logger.info("Inspection resources registered")
