#!/usr/bin/env python3
"""
DaVinci Resolve MCP Core Tools
Version info and page navigation
"""


def register_core_tools(mcp, resolve, logger):
    """Register core MCP tools."""

    @mcp.tool()
    def reconnect_resolve() -> str:
        """Retry connection to DaVinci Resolve if it was lost or not established.

        Returns:
            str: Connection status message.
        """
        # Try to find the manager in the global scope if possible
        # In this architecture, we might need a better way to share it,
        # but for now, we'll try to re-initialize via the core logic.
        try:
            import importlib

            resolve_manager = importlib.import_module(
                "src.utils.resolve_manager"
            ).resolve_manager

            if resolve_manager.connect():
                return f"Successfully reconnected to DaVinci Resolve: {resolve_manager.instance.GetProductName()}"
            else:
                return "Failed to reconnect. Ensure DaVinci Resolve is running and External Scripting is enabled."
        except ImportError:
            # Fallback if manager isn't easily accessible
            return "Reconnection tool error: Could not access connection manager."

    # @mcp.tool() - SKIPPED: switch_page is in granular (prefer upstream)
    def switch_page(page: str) -> str:
        """Switch to a specific page in DaVinci Resolve.

        Args:
            page: The page to switch to. Options: 'media', 'cut', 'edit', 'fusion', 'color', 'fairlight', 'deliver'

        Returns:
            str: A message indicating the success or failure of the page switch operation.
                - On success: "Successfully switched to {page} page"
                - On failure: An error message describing the issue.
        """
        # Try to get fresh resolve instance
        current_resolve = resolve
        try:
            import importlib

            resolve_manager = importlib.import_module(
                "src.utils.resolve_manager"
            ).resolve_manager

            current_resolve = resolve_manager.instance
        except ImportError:
            pass

        if not current_resolve:
            return "Error: Not connected to DaVinci Resolve. Try calling 'reconnect_resolve' tool first."

        valid_pages = [
            "media",
            "cut",
            "edit",
            "fusion",
            "color",
            "fairlight",
            "deliver",
        ]
        page_lower = page.lower()

        if page_lower not in valid_pages:
            return f"Error: Invalid page name. Must be one of: {', '.join(valid_pages)}"

        result = current_resolve.OpenPage(page_lower)
        if result:
            return f"Successfully switched to {page_lower} page"
        else:
            return f"Failed to switch to {page_lower} page"

    logger.info("Registered core tools")
