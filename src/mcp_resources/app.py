#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Application related resources
"""

from typing import Any

from fastmcp.resources import ResourceContent, ResourceResult
from src.utils.app_control import get_app_state


def register_app_resources(mcp, resolve, logger):
    """Register application-related resources."""

    def to_resource_result(payload: Any) -> ResourceResult:
        return ResourceResult([ResourceContent(payload)])

    @mcp.resource("resolve://app/state")
    def get_app_state_endpoint() -> ResourceResult:
        """Get DaVinci Resolve application state information via API inspection.

        Returns:
            Dict[str, Any]: A dictionary containing connection status, product name, and version.
        """
        if resolve is None:
            return to_resource_result(
                {"error": "Not connected to DaVinci Resolve", "connected": False}
            )

        return to_resource_result(get_app_state(resolve))

    @mcp.resource("resolve://app/screenshot")
    def get_app_screenshot() -> ResourceResult:
        """Capture a screenshot of the DaVinci Resolve window (macOS only).

        Returns:
            str: Path to the saved screenshot file, or an error message.
        """
        from src.utils.screenshot import capture_resolve_window_mac

        return to_resource_result(capture_resolve_window_mac())

    @mcp.resource("resolve://version")
    def get_resolve_version() -> ResourceResult:
        """Get DaVinci Resolve version information."""
        if resolve is None:
            return to_resource_result("Error: Not connected to DaVinci Resolve")
        return to_resource_result(
            f"{resolve.GetProductName()} {resolve.GetVersionString()}"
        )

    @mcp.resource("resolve://pages")
    def list_pages() -> ResourceResult:
        """List all available pages in DaVinci Resolve."""
        return to_resource_result(
            [
                "media",
                "cut",
                "edit",
                "fusion",
                "color",
                "fairlight",
                "deliver",
            ]
        )

    @mcp.resource("resolve://current-page")
    def get_current_page() -> ResourceResult:
        """Get the currently active page in DaVinci Resolve."""
        if resolve is None:
            return to_resource_result("Error: Not connected to DaVinci Resolve")
        return to_resource_result(resolve.GetCurrentPage())

    @mcp.resource("resolve://is-project-manager-open")
    def is_project_manager_open() -> ResourceResult:
        """Check if the project manager is currently open."""
        if resolve is None:
            return to_resource_result(False)
        pm = resolve.GetProjectManager()
        return to_resource_result(pm is not None)

    logger.info("Application resources registered")
