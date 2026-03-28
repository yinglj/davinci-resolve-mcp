"""
Capture Tool Registration for DaVinci Resolve MCP Server.

Registers screenshot capture tools for AI agents to "see" DaVinci Resolve.
"""

from typing import Any, Dict, Optional

from fastmcp.resources import ResourceContent, ResourceResult


def register_capture_tools(mcp):
    """Register screenshot capture tools."""
    from src.utils.capture import (
        capture_screenshot,
        capture_window,
        capture_resolve_window,
        list_windows,
        find_resolve_window,
        get_monitor_info,
        is_wsl,
    )
    from src.utils.capture_continuous import (
        start_monitoring,
        stop_monitoring,
        get_monitoring_status,
    )

    def to_resource_result(payload: Any) -> ResourceResult:
        return ResourceResult([ResourceContent(payload)])

    @mcp.tool()
    def take_screenshot(
        output_path: Optional[str] = None,
        quality: int = 85,
        monitor_id: int = 0,
        capture_all: bool = False,
        return_base64: bool = False,
    ) -> Dict[str, Any]:
        """
        Take a screenshot of the Windows desktop.

        Args:
            output_path: Path to save screenshot (auto-generated if None)
            quality: JPEG quality (1-100)
            monitor_id: Monitor index (0-based)
            capture_all: Capture all monitors combined
            return_base64: Return image as base64 instead of saving

        Returns:
            Dict with success status and path or base64 data
        """
        kwargs: Dict[str, Any] = {
            "quality": quality,
            "monitor_id": monitor_id,
            "capture_all": capture_all,
            "return_base64": return_base64,
        }
        if output_path is not None:
            kwargs["output_path"] = output_path
        return capture_screenshot(**kwargs)

    @mcp.tool()
    def capture_resolve_ui(
        output_path: Optional[str] = None,
        quality: int = 85,
        return_base64: bool = False,
    ) -> Dict[str, Any]:
        """
        Capture screenshot of the DaVinci Resolve window.

        Args:
            output_path: Path to save screenshot (auto-generated if None)
            quality: JPEG quality (1-100)
            return_base64: Return image as base64 instead of saving

        Returns:
            Dict with success status and path or base64 data
        """
        kwargs: Dict[str, Any] = {
            "quality": quality,
            "return_base64": return_base64,
        }
        if output_path is not None:
            kwargs["output_path"] = output_path
        return capture_resolve_window(**kwargs)

    @mcp.tool()
    def capture_window_by_handle(
        window_handle: int,
        output_path: Optional[str] = None,
        quality: int = 85,
        return_base64: bool = False,
    ) -> Dict[str, Any]:
        """
        Capture a specific window by its handle.

        Args:
            window_handle: Window handle from list_all_windows
            output_path: Path to save screenshot
            quality: JPEG quality (1-100)
            return_base64: Return image as base64 instead of saving

        Returns:
            Dict with success status and path or base64 data
        """
        kwargs: Dict[str, Any] = {
            "window_handle": window_handle,
            "quality": quality,
            "return_base64": return_base64,
        }
        if output_path is not None:
            kwargs["output_path"] = output_path
        return capture_window(**kwargs)

    @mcp.resource("resolve://system/windows")
    def list_all_windows() -> ResourceResult:
        """List all visible windows with their handles."""
        return to_resource_result(list_windows())

    @mcp.resource("resolve://system/monitors")
    def get_all_monitors() -> ResourceResult:
        """Get information about all monitors."""
        return to_resource_result(get_monitor_info())

    @mcp.resource("resolve://system/resolve-window")
    def get_resolve_window_info() -> ResourceResult:
        """Find DaVinci Resolve window information."""
        window = find_resolve_window()
        if window:
            return to_resource_result({"success": True, "window": window})
        return to_resource_result(
            {"success": False, "error": "DaVinci Resolve window not found"}
        )

    @mcp.resource("resolve://system/environment")
    def get_environment_info() -> ResourceResult:
        """Get system environment information."""
        import sys
        import os

        return to_resource_result(
            {
                "is_wsl": is_wsl(),
                "platform": sys.platform,
                "python_version": sys.version,
                "cwd": os.getcwd(),
            }
        )

    @mcp.tool()
    def start_screenshot_monitoring(
        output_dir: Optional[str] = None,
        interval_sec: float = 1.0,
        quality: int = 60,
        monitor_id: int = 0,
        capture_all: bool = False,
    ) -> Dict[str, Any]:
        """
        Start continuous screenshot monitoring.

        Args:
            output_dir: Directory to save screenshots
            interval_sec: Seconds between screenshots
            quality: JPEG quality (1-100)
            monitor_id: Monitor index (0-based)
            capture_all: Capture all monitors combined

        Returns:
            Dict with success status and session info
        """
        kwargs: Dict[str, Any] = {
            "interval_sec": interval_sec,
            "quality": quality,
            "monitor_id": monitor_id,
            "capture_all": capture_all,
        }
        if output_dir:
            kwargs["output_dir"] = output_dir
        return start_monitoring(**kwargs)

    @mcp.tool()
    def stop_screenshot_monitoring() -> Dict[str, Any]:
        """Stop continuous screenshot monitoring."""
        return stop_monitoring()

    @mcp.resource("resolve://system/monitoring-status")
    def get_screenshot_monitoring_status() -> ResourceResult:
        """Get current screenshot monitoring status."""
        return to_resource_result(get_monitoring_status())
