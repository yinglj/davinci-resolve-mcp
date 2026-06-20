#!/usr/bin/env python3
"""DaVinci Resolve MCP - Layout Operations (Granular Tools)."""

from typing import Any, Dict, List, Optional, Union, Tuple
from .common import mcp, get_resolve

@mcp.tool()
def save_layout_preset_tool(preset_name: str) -> Dict[str, Any]:
    """Save the current UI layout as a preset.

    Calls Resolve.SaveLayoutPreset() to save the current UI layout.

    Args:
        preset_name: Name for the saved preset.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    result = resolve.SaveLayoutPreset(preset_name)
    return {"success": bool(result), "preset_name": preset_name}

@mcp.tool()
def load_layout_preset_tool(preset_name: str) -> Dict[str, Any]:
    """Load a UI layout preset.

    Calls Resolve.LoadLayoutPreset() to load a saved UI layout.

    Args:
        preset_name: Name of the preset to load.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    result = resolve.LoadLayoutPreset(preset_name)
    return {"success": bool(result), "preset_name": preset_name}

@mcp.tool()
def export_layout_preset_tool(preset_name: str, export_path: str) -> Dict[str, Any]:
    """Export a layout preset to a file.

    Calls Resolve.ExportLayoutPreset() to export a preset to disk.

    Args:
        preset_name: Name of the preset to export.
        export_path: Absolute file path to export the preset to.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    result = resolve.ExportLayoutPreset(preset_name, export_path)
    return {"success": bool(result), "preset_name": preset_name, "export_path": export_path}

@mcp.tool()
def import_layout_preset_tool(import_path: str, preset_name: str = None) -> Dict[str, Any]:
    """Import a layout preset from a file.

    Calls Resolve.ImportLayoutPreset() to import a preset from disk.

    Args:
        import_path: Absolute path to the preset file to import.
        preset_name: Name to save the imported preset as (uses filename if None).
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    if preset_name:
        result = resolve.ImportLayoutPreset(import_path, preset_name)
    else:
        result = resolve.ImportLayoutPreset(import_path)
        preset_name = os.path.splitext(os.path.basename(import_path))[0]
    return {"success": bool(result), "preset_name": preset_name, "import_path": import_path}

@mcp.tool()
def delete_layout_preset_tool(preset_name: str) -> Dict[str, Any]:
    """Delete a layout preset.

    Calls Resolve.DeleteLayoutPreset() to remove a saved preset.

    Args:
        preset_name: Name of the preset to delete.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    result = resolve.DeleteLayoutPreset(preset_name)
    return {"success": bool(result), "preset_name": preset_name}

# ------------------
# App Control
# ------------------

@mcp.resource("resolve://app/state")
def get_app_state_endpoint() -> Dict[str, Any]:
    """Get DaVinci Resolve application state information."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve", "connected": False}
    
    return get_app_state(resolve)

@mcp.tool()
def update_layout_preset(preset_name: str) -> Dict[str, Any]:
    """Overwrite an existing layout preset with the current UI layout.

    Args:
        preset_name: Name of the preset to overwrite.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    result = resolve.UpdateLayoutPreset(preset_name)
    return {"success": bool(result), "preset_name": preset_name}

