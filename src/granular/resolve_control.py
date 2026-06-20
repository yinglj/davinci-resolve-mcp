#!/usr/bin/env python3
"""DaVinci Resolve MCP - Resolve_Control Operations (Granular Tools)."""

from typing import Any, Dict, List, Optional, Union, Tuple
from .common import mcp, get_resolve

@mcp.tool()
def switch_page(page: str) -> str:
    """Switch to a specific page in DaVinci Resolve.
    
    Args:
        page: The page to switch to. Options: 'media', 'cut', 'edit', 'fusion', 'color', 'fairlight', 'deliver'
    """
    resolve = get_resolve()
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    valid_pages = ['media', 'cut', 'edit', 'fusion', 'color', 'fairlight', 'deliver']
    page = page.lower()
    
    if page not in valid_pages:
        return f"Error: Invalid page name. Must be one of: {', '.join(valid_pages)}"
    
    result = resolve.OpenPage(page)
    if result:
        return f"Successfully switched to {page} page"
    else:
        return f"Failed to switch to {page} page"

# ------------------
# Project Management
# ------------------

@mcp.resource("resolve://projects")
def list_projects() -> List[str]:
    """List all available projects in the current database."""
    project_manager = get_project_manager()
    if not project_manager:
        return ["Error: Failed to get Project Manager"]
    
    projects = project_manager.GetProjectListInCurrentFolder()
    
    # Filter out any empty strings that might be in the list
    return [p for p in projects if p]

@mcp.resource("resolve://current-project")
def get_current_project_name() -> str:
    """Get the name of the currently open project."""
    pm, current_project = get_current_project()
    if not current_project:
        return "No project currently open"
    
    return current_project.GetName()

@mcp.resource("resolve://project-settings")
def get_project_settings() -> Dict[str, Any]:
    """Get all project settings from the current project."""
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    try:
        # Get all settings
        return current_project.GetSetting('')
    except Exception as e:
        return {"error": f"Failed to get project settings: {str(e)}"}

@mcp.resource("resolve://project-setting/{setting_name}")
def get_project_setting(setting_name: str) -> Dict[str, Any]:
    """Get a specific project setting by name.
    
    Args:
        setting_name: The specific setting to retrieve.
    """
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    try:
        # Get specific setting
        value = current_project.GetSetting(setting_name)
        return {setting_name: value}
    except Exception as e:
        return {"error": f"Failed to get project setting '{setting_name}': {str(e)}"}

@mcp.tool()
def object_help(object_type: str) -> str:
    """
    Get human-readable help for a DaVinci Resolve API object.
    
    Args:
        object_type: Type of object to get help for ('resolve', 'project_manager', 
                     'project', 'media_pool', 'timeline', 'media_storage')
    """
    resolve = get_resolve()
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    # Map object type string to actual object
    obj = None
    
    if object_type == 'resolve':
        obj = resolve
    elif object_type == 'project_manager':
        obj = resolve.GetProjectManager()
    elif object_type == 'project':
        pm = resolve.GetProjectManager()
        if pm:
            obj = pm.GetCurrentProject()
    elif object_type == 'media_pool':
        pm = resolve.GetProjectManager()
        if pm:
            project = pm.GetCurrentProject()
            if project:
                obj = project.GetMediaPool()
    elif object_type == 'timeline':
        pm = resolve.GetProjectManager()
        if pm:
            project = pm.GetCurrentProject()
            if project:
                obj = project.GetCurrentTimeline()
    elif object_type == 'media_storage':
        obj = resolve.GetMediaStorage()
    else:
        return f"Error: Unknown object type '{object_type}'"
    
    if obj is None:
        return f"Error: Failed to get {object_type} object"
    
    # Generate and return help text
    return print_object_help(obj)

@mcp.tool()
def inspect_custom_object(object_path: str) -> Dict[str, Any]:
    """
    Inspect a custom DaVinci Resolve API object by path.
    
    Args:
        object_path: Path to the object using dot notation (e.g., 'resolve.GetMediaStorage()')
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    
    try:
        # Start with resolve object
        obj = resolve
        
        # Split the path and traverse down
        parts = object_path.split('.')
        
        # Skip the first part if it's 'resolve'
        start_index = 1 if parts[0].lower() == 'resolve' else 0
        
        for i in range(start_index, len(parts)):
            part = parts[i]
            
            # Check if it's a method call
            if part.endswith('()'):
                method_name = part[:-2]
                if hasattr(obj, method_name) and callable(getattr(obj, method_name)):
                    obj = getattr(obj, method_name)()
                else:
                    return {"error": f"Method '{method_name}' not found or not callable"}
            else:
                # It's an attribute access
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                else:
                    return {"error": f"Attribute '{part}' not found"}
        
        # Inspect the object we've retrieved
        return inspect_object(obj)
    except Exception as e:
        return {"error": f"Error inspecting object: {str(e)}"}

# ------------------
# Layout Presets
# ------------------

@mcp.resource("resolve://layout-presets")
def get_layout_presets() -> List[Dict[str, Any]]:
    """Get all available layout presets for DaVinci Resolve."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    
    return list_layout_presets(layout_type="ui")

@mcp.tool()
def quit_app(force: bool = False, save_project: bool = True) -> str:
    """
    Quit DaVinci Resolve application.
    
    Args:
        force: Whether to force quit even if unsaved changes (potentially dangerous)
        save_project: Whether to save the project before quitting
    """
    resolve = get_resolve()
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    result = quit_resolve_app(resolve, force, save_project)
    
    if result:
        return "DaVinci Resolve quit command sent successfully"
    else:
        return "Failed to quit DaVinci Resolve"

@mcp.tool()
def restart_app(wait_seconds: int = 5) -> str:
    """
    Restart DaVinci Resolve application.
    
    Args:
        wait_seconds: Seconds to wait between quit and restart
    """
    resolve = get_resolve()
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    result = restart_resolve_app(resolve, wait_seconds)
    
    if result:
        return "DaVinci Resolve restart initiated successfully"
    else:
        return "Failed to restart DaVinci Resolve"

@mcp.tool()
def open_settings() -> str:
    """Open the Project Settings dialog in DaVinci Resolve."""
    resolve = get_resolve()
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    result = open_project_settings(resolve)
    
    if result:
        return "Project Settings dialog opened successfully"
    else:
        return "Failed to open Project Settings dialog"

@mcp.tool()
def open_app_preferences() -> str:
    """Open the Preferences dialog in DaVinci Resolve."""
    resolve = get_resolve()
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    result = open_preferences(resolve)
    
    if result:
        return "Preferences dialog opened successfully"
    else:
        return "Failed to open Preferences dialog"

# ------------------
# Cloud Project Operations
# ------------------

@mcp.resource("resolve://cloud/projects")
def get_cloud_projects() -> Dict[str, Any]:
    """Get list of available cloud projects."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve", "success": False}
    
    return get_cloud_project_list(resolve)

@mcp.tool()
def get_resolve_version_fields() -> Dict[str, Any]:
    """Get DaVinci Resolve version as structured fields [major, minor, patch, build, suffix]."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    version = resolve.GetVersion()
    if version:
        return {"major": version[0], "minor": version[1], "patch": version[2], "build": version[3], "suffix": version[4] if len(version) > 4 else ""}
    return {"error": "Failed to get version"}

@mcp.tool()
def get_fusion_object() -> Dict[str, Any]:
    """Get the Fusion object. Starting point for Fusion scripts."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    fusion = resolve.Fusion()
    if fusion:
        return {"success": True, "fusion_available": True}
    return {"success": False, "fusion_available": False}

@mcp.tool()
def get_keyframe_mode() -> Dict[str, Any]:
    """Get the current keyframe mode in Resolve. Returns 0=ALL, 1=COLOR, 2=SIZING."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    mode = resolve.GetKeyframeMode()
    mode_names = {0: "All", 1: "Color", 2: "Sizing"}
    return {"keyframe_mode": mode, "mode_name": mode_names.get(mode, "Unknown")}

@mcp.tool()
def set_keyframe_mode(mode: int) -> Dict[str, Any]:
    """Set the keyframe mode in Resolve.

    Args:
        mode: Keyframe mode - 0=All, 1=Color, 2=Sizing.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    if mode not in (0, 1, 2):
        return {"error": "Invalid mode. Must be 0 (All), 1 (Color), or 2 (Sizing)"}
    result = resolve.SetKeyframeMode(mode)
    mode_names = {0: "All", 1: "Color", 2: "Sizing"}
    return {"success": bool(result), "keyframe_mode": mode, "mode_name": mode_names[mode]}

@mcp.tool()
def quit_resolve() -> Dict[str, Any]:
    """Quit DaVinci Resolve. WARNING: This will close the application."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    result = resolve.Quit()
    return {"success": True, "message": "DaVinci Resolve is quitting"}


# ------------------
# ProjectManager Tools (missing methods)
# ------------------

