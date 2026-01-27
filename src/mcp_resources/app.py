#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Application related resources
"""

from typing import Dict, Any


def register_app_resources(mcp, resolve, logger):
    """Register application-related resources."""

    @mcp.resource("resolve://version")
    def get_resolve_version() -> str:
        """Get DaVinci Resolve version information."""
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        return f"{resolve.GetProductName()} {resolve.GetVersionString()}"

    @mcp.resource("resolve://pages")
    def list_pages() -> list[str]:
        """List all available pages in DaVinci Resolve."""
        return ["media", "cut", "edit", "fusion", "color", "fairlight", "deliver"]

    @mcp.resource("resolve://current-page")
    def get_current_page() -> str:
        """Get the currently active page in DaVinci Resolve."""
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        return resolve.GetCurrentPage()

    @mcp.resource("resolve://is-project-manager-open")
    def is_project_manager_open() -> bool:
        """Check if the project manager is currently open."""
        if resolve is None:
            return False
        pm = resolve.GetProjectManager()
        return pm is not None

    logger.info("Application resources registered")
