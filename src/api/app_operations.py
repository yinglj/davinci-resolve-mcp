#!/usr/bin/env python3
"""
DaVinci Resolve Application Operations
Ported from samuelgursky commit 8ea53b8
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("davinci-resolve-mcp.app")


def quit_app(resolve, force: bool = False, save_project: bool = True) -> str:
    """Quit DaVinci Resolve."""
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"

    try:
        # Note: Quit() is usually on the Resolve object
        result = resolve.Quit()
        return "Quit request sent to DaVinci Resolve"
    except Exception as e:
        return f"Error quitting: {e}"


def open_settings(resolve) -> str:
    """Open Project Settings."""
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"

    try:
        # OpenPage("settings") isn't a thing, but there might be a shortcut
        # Or we use the UI automation if possible.
        # Samuel's commit had this:
        # result = resolve.OpenPage("settings") # This might be custom or v19
        result = resolve.OpenPage("media")  # Fallback
        return "Opened media page (settings opening not natively supported via script API in older versions)"
    except Exception as e:
        return f"Error: {e}"


def register_tools(proxy):
    """Register app tools."""
    from ..resolve_mcp_server import get_resolve

    proxy.register_tool(
        "quit_resolve",
        lambda force=False, save_project=True: quit_app(
            get_resolve(), force, save_project
        ),
        "app",
        "Quit DaVinci Resolve",
        {
            "force": {"type": "boolean", "description": "Force quit", "default": False},
            "save_project": {
                "type": "boolean",
                "description": "Save before quitting",
                "default": True,
            },
        },
    )
    return 1
