#!/usr/bin/env python3
"""
Mac-specific screenshot utility for DaVinci Resolve MCP Server
"""

import os
import subprocess
import tempfile
import time
import logging

logger = logging.getLogger("davinci-resolve-mcp.screenshot")


def capture_resolve_window_mac(output_path: str = None) -> dict:
    """
    Captures the DaVinci Resolve window on macOS.

    Args:
        output_path: Optional path to save the screenshot. If None, a temporary file is created.

    Returns:
        Dictionary with success status and file path.
    """
    if not output_path:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(
            temp_dir, f"resolve_screenshot_{int(time.time())}.png"
        )

    try:
        # 1. Bring DaVinci Resolve to front first to ensure it's visible
        # This uses AppleScript to find the process and activate it
        applescript = 'tell application "System Events" to set frontmost of process "DaVinci Resolve" to true'
        subprocess.run(["osascript", "-e", applescript], capture_output=True)

        # Give it a tiny bit of time to come to front
        time.sleep(0.5)

        # 2. Capture the window
        # First, we try to find the window ID for DaVinci Resolve to capture ONLY that window
        # If we can't find it, we'll just capture the whole screen or a selection

        # Simple approach for now: capture the frontmost window (which we just set to Resolve)
        # -W: capture only the window
        # -i: interactive (not good for us)
        # -x: no sound
        # -l: Capture window with ID

        # To get the window ID on Mac is a bit complex via command line without extra tools,
        # so we use a more robust AppleScript approach or just capture the screen.

        # Efficient way: Use screencapture for the whole screen if Resolve is frontmost
        result = subprocess.run(
            ["screencapture", "-x", output_path], capture_output=True
        )

        if result.returncode == 0 and os.path.exists(output_path):
            return {
                "success": True,
                "path": output_path,
                "message": f"Successfully captured screenshot to {output_path}",
            }
        else:
            return {
                "success": False,
                "error": f"screencapture failed with code {result.returncode}: {result.stderr.decode()}",
            }

    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}")
        return {"success": False, "error": str(e)}


def get_resolve_window_bounds_mac():
    """
    Get the bounds of the DaVinci Resolve window using AppleScript.
    """
    applescript = """
    tell application "System Events"
        tell process "DaVinci Resolve"
            if exists window 1 then
                return bounds of window 1
            else
                return "error"
            end if
        end tell
    end tell
    """
    result = subprocess.run(
        ["osascript", "-e", applescript], capture_output=True, text=True
    )
    if result.stdout.strip() == "error" or not result.stdout.strip():
        return None

    # Format: "x1, y1, x2, y2"
    try:
        bounds = [int(x.strip()) for x in result.stdout.strip().split(",")]
        return bounds
    except:
        return None
