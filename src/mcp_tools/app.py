#!/usr/bin/env python3
"""
DaVinci Resolve MCP App Control Tools
Application state, quit, restart, and settings
"""

from typing import Dict, Any

from src.utils.app_control import (
    quit_resolve_app,
    get_app_state,
    restart_resolve_app,
    open_project_settings,
    open_preferences,
)


def register_app_tools(mcp, resolve, logger):
    """Register app control MCP tools and resources."""

    @mcp.resource("resolve://app/state")
    def get_app_state_endpoint() -> Dict[str, Any]:
        """Get DaVinci Resolve application state information via API inspection.

        Returns:
            Dict[str, Any]: A dictionary containing connection status, product name, and version.
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve", "connected": False}

        return get_app_state(resolve)

    @mcp.resource("resolve://app/screenshot")
    def get_app_screenshot() -> str:
        """Capture a screenshot of the DaVinci Resolve window (macOS only).

        Returns:
            str: Path to the saved screenshot file, or an error message.
        """
        from src.utils.screenshot import capture_resolve_window_mac

        return capture_resolve_window_mac()

    @mcp.tool()
    def quit_app(force: bool = False, save_project: bool = True) -> str:
        """Quit DaVinci Resolve application.

        Args:
            force: Whether to force quit even if unsaved changes (potentially dangerous)
            save_project: Whether to save the project before quitting

        Returns:
            str: Status message of the quit operation.
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"

        result = quit_resolve_app(resolve, force, save_project)

        if result:
            return "DaVinci Resolve quit command sent successfully"
        else:
            return "Failed to quit DaVinci Resolve"

    @mcp.tool()
    def restart_app(wait_seconds: int = 5) -> str:
        """Restart DaVinci Resolve application.

        Args:
            wait_seconds: Seconds to wait between quit and restart

        Returns:
            str: Status message of the restart operation.
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"

        result = restart_resolve_app(resolve, wait_seconds)

        if result:
            return "DaVinci Resolve restart initiated successfully"
        else:
            return "Failed to restart DaVinci Resolve"

    @mcp.tool()
    def open_settings() -> str:
        """Open the Project Settings dialog in DaVinci Resolve.

        Returns:
            str: Status message of the settings operation.
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"

        result = open_project_settings(resolve)

        if result:
            return "Project Settings dialog opened successfully"
        else:
            return "Failed to open Project Settings dialog"

    @mcp.tool()
    def open_app_preferences() -> str:
        """Open the Preferences dialog in DaVinci Resolve.

        Returns:
            str: Status message of the preferences operation.
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"

        result = open_preferences(resolve)

        if result:
            return "Preferences dialog opened successfully"
        else:
            return "Failed to open Preferences dialog"

    logger.info("Registered app tools")
