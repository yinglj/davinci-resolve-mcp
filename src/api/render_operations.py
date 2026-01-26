#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server - Color Operations Utilities

This module provides functions for working with DaVinci Resolve color operations.
"""

import logging
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger("davinci-resolve-mcp.render")


def add_to_render_queue(
    resolve, preset_name: str, timeline_name: str = None
) -> Dict[str, Any]:
    """Add a timeline to the render queue with a specific preset."""
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        return {"success": False, "error": "No project open"}

    # Find project timeline
    timeline = None
    if timeline_name:
        for i in range(1, project.GetTimelineCount() + 1):
            t = project.GetTimelineByIndex(i)
            if t.GetName() == timeline_name:
                timeline = t
                break
        if not timeline:
            return {"success": False, "error": f"Timeline '{timeline_name}' not found"}
    else:
        timeline = project.GetCurrentTimeline()

    if not timeline:
        return {"success": False, "error": "No timeline active"}

    try:
        # Load the render preset
        if not project.LoadRenderPreset(preset_name):
            return {
                "success": False,
                "error": f"Render preset '{preset_name}' not found",
            }

        # Add to queue
        result = project.AddRenderJob()
        return {
            "success": bool(result),
            "timeline": timeline.GetName(),
            "preset": preset_name,
            "job_id": result if result else None,
        }
    except Exception as e:
        logger.error(f"Error adding to render queue: {e}")
        return {"success": False, "error": str(e)}


def start_render(resolve) -> Dict[str, Any]:
    """Start rendering jobs in the queue."""
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        return {"success": False, "error": "No project open"}

    try:
        result = project.StartRendering()
        return {"success": bool(result), "message": "Rendering started"}
    except Exception as e:
        logger.error(f"Error starting render: {e}")
        return {"success": False, "error": str(e)}


def register_tools(proxy):
    """Register render tools."""
    from ..resolve_mcp_server import get_resolve

    proxy.register_tool(
        "add_to_render_queue",
        lambda preset_name, timeline_name=None: add_to_render_queue(
            get_resolve(), preset_name, timeline_name
        ),
        "delivery",
        "Add a timeline to the render queue with a specified preset",
        {
            "preset_name": {
                "type": "string",
                "description": "Name of the render preset (e.g., 'YouTube 1080p')",
            },
            "timeline_name": {
                "type": "string",
                "description": "Optional timeline name (uses current if omitted)",
                "optional": True,
            },
        },
    )

    proxy.register_tool(
        "start_render",
        lambda: start_render(get_resolve()),
        "delivery",
        "Start rendering all jobs in the render queue",
        {},
    )
    return 2
