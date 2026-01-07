#!/usr/bin/env python3
"""
DaVinci Resolve Project Operations
Ported from samuelgursky commit 8ea53b8
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("davinci-resolve-mcp.project")


def set_project_setting(resolve, setting_name: str, value: Any) -> str:
    """Set a project setting."""
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        return "Error: No project open"

    try:
        result = project.SetSetting(setting_name, str(value))
        return (
            f"Successfully set '{setting_name}' to '{value}'"
            if result
            else f"Failed to set '{setting_name}'"
        )
    except Exception as e:
        return f"Error: {e}"


def set_timeline_format(resolve, width: int, height: int, frame_rate: float) -> str:
    """Set timeline resolution and frame rate."""
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        return "Error: No project open"

    try:
        r1 = project.SetSetting("timelineResolutionWidth", str(width))
        r2 = project.SetSetting("timelineResolutionHeight", str(height))
        r3 = project.SetSetting("timelineFrameRate", str(frame_rate))
        return f"Successfully set timeline format to {width}x{height} @ {frame_rate}fps"
    except Exception as e:
        return f"Error: {e}"


def register_tools(proxy):
    """Register project tools."""
    from ..resolve_mcp_server import get_resolve

    proxy.register_tool(
        "set_project_setting",
        lambda setting_name, value: set_project_setting(
            get_resolve(), setting_name, value
        ),
        "project",
        "Set a specific project setting",
        {
            "setting_name": {
                "type": "string",
                "description": "Internal name of the setting",
            },
            "value": {"type": "string", "description": "New value"},
        },
    )

    proxy.register_tool(
        "set_timeline_format",
        lambda width, height, frame_rate: set_timeline_format(
            get_resolve(), width, height, frame_rate
        ),
        "project",
        "Set timeline resolution and frame rate",
        {
            "width": {"type": "integer", "description": "Width in pixels"},
            "height": {"type": "integer", "description": "Height in pixels"},
            "frame_rate": {"type": "number", "description": "Frame rate"},
        },
    )
    return 2
